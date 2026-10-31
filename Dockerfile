# syntax=docker/dockerfile:1.7
# ---------------------------------------------------------------------------
# FinSecure Pay - Transaction Validation API
# Multi-stage build: (1) compile & package with Maven, (2) extract Spring Boot
# layers, (3) minimal non-root JRE runtime image.
# ---------------------------------------------------------------------------

# ---------- Stage 1: build ----------
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml .
COPY security ./security
# Cache dependencies in a separate layer
RUN --mount=type=cache,target=/root/.m2 mvn -B -q dependency:go-offline
COPY src ./src
# Tests are executed by the CI pipeline before the image is built
RUN --mount=type=cache,target=/root/.m2 mvn -B -q package -DskipTests

# ---------- Stage 2: extract layers ----------
FROM eclipse-temurin:21-jre-alpine AS extract
WORKDIR /workspace
COPY --from=build /workspace/target/finsecure-pay.jar app.jar
RUN java -Djarmode=tools -jar app.jar extract --layers --destination extracted

# ---------- Stage 3: runtime ----------
FROM eclipse-temurin:21-jre-alpine

ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
LABEL org.opencontainers.image.title="finsecure-pay" \
      org.opencontainers.image.description="FinSecure Pay transaction validation API" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.vendor="FinSecure Pay"

# Patch OS packages and create an unprivileged user
RUN apk upgrade --no-cache \
    && addgroup -S -g 10001 app \
    && adduser -S -u 10001 -G app -h /app app

WORKDIR /app
COPY --from=extract --chown=app:app /workspace/extracted/dependencies/ ./
COPY --from=extract --chown=app:app /workspace/extracted/spring-boot-loader/ ./
COPY --from=extract --chown=app:app /workspace/extracted/snapshot-dependencies/ ./
COPY --from=extract --chown=app:app /workspace/extracted/application/ ./

USER 10001:10001
EXPOSE 8080

ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError -Djava.security.egd=file:/dev/./urandom" \
    APP_VERSION=${APP_VERSION}

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health/liveness || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
