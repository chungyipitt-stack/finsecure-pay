package com.finsecure.pay.controller;

import java.time.Clock;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.info.BuildProperties;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Lightweight business-level health endpoint used for smoke tests and demos.
 * Kubernetes probes use the Actuator liveness/readiness groups instead.
 */
@RestController
public class HealthController {

    private final String version;
    private final String environment;
    private final String serviceName;
    private final Clock clock;

    public HealthController(ObjectProvider<BuildProperties> buildProperties,
                            @Value("${spring.application.name}") String serviceName,
                            @Value("${app.environment:local}") String environment,
                            @Value("${APP_VERSION:}") String imageVersion,
                            Clock clock) {
        BuildProperties bp = buildProperties.getIfAvailable();
        String buildVersion = bp != null ? bp.getVersion() : "unknown";
        // APP_VERSION is baked into the container image as the image tag (e.g. 1.0.0-15-a1b2c3d)
        this.version = (imageVersion == null || imageVersion.isBlank() || "dev".equals(imageVersion))
                ? buildVersion : imageVersion;
        this.serviceName = serviceName;
        this.environment = environment;
        this.clock = clock;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("status", "UP");
        body.put("service", serviceName);
        body.put("version", version);
        body.put("environment", environment);
        body.put("timestamp", Instant.now(clock).toString());
        return body;
    }
}
