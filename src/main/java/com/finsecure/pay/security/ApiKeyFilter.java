package com.finsecure.pay.security;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Protects POST /validate with a shared API key supplied in the {@code X-API-Key} header.
 *
 * <p>The key is never stored in source control: in Kubernetes it is injected from a
 * Kubernetes Secret (FINSECURE_API_KEY) that Jenkins creates from its credential store.
 * When no key is configured (local development / unit tests) the filter is a no-op.
 */
@Component
public class ApiKeyFilter extends OncePerRequestFilter {

    public static final String HEADER = "X-API-Key";
    private static final Logger log = LoggerFactory.getLogger(ApiKeyFilter.class);

    private final byte[] expectedKey;

    public ApiKeyFilter(@Value("${finsecure.security.api-key:}") String apiKey) {
        this.expectedKey = apiKey == null || apiKey.isBlank() ? null : apiKey.getBytes(StandardCharsets.UTF_8);
        if (expectedKey == null) {
            log.warn("No API key configured - /validate is UNAUTHENTICATED (acceptable for local development only)");
        }
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return expectedKey == null || !request.getRequestURI().startsWith("/validate");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String provided = request.getHeader(HEADER);
        if (provided != null
                && MessageDigest.isEqual(expectedKey, provided.getBytes(StandardCharsets.UTF_8))) {
            chain.doFilter(request, response);
            return;
        }
        log.warn("Rejected request to {} from {}: missing or invalid API key", request.getRequestURI(),
                request.getRemoteAddr());
        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write("{\"status\":401,\"code\":\"UNAUTHORIZED\",\"message\":\"Missing or invalid API key\"}");
    }
}
