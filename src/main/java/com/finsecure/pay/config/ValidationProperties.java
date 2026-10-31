package com.finsecure.pay.config;

import java.math.BigDecimal;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

/**
 * Externalised validation rules. In Kubernetes these are supplied by a ConfigMap
 * (e.g. FINSECURE_VALIDATION_MAX_AMOUNT, FINSECURE_VALIDATION_SUPPORTED_CURRENCIES).
 *
 * @param maxAmount           maximum value allowed for a single transaction
 * @param minAmount           minimum value allowed for a single transaction
 * @param supportedCurrencies ISO-4217 currency codes accepted by the platform
 * @param blockedAccounts     accounts flagged by compliance (sanctions / fraud)
 * @param maxFutureSkewSeconds tolerated clock skew for client timestamps
 */
@ConfigurationProperties(prefix = "finsecure.validation")
public record ValidationProperties(
        @DefaultValue("10000.00") BigDecimal maxAmount,
        @DefaultValue("0.01") BigDecimal minAmount,
        @DefaultValue({"SGD", "USD", "EUR", "MYR"}) List<String> supportedCurrencies,
        @DefaultValue({}) List<String> blockedAccounts,
        @DefaultValue("300") long maxFutureSkewSeconds) {

    public Set<String> supportedCurrencySet() {
        return supportedCurrencies.stream()
                .map(c -> c.trim().toUpperCase())
                .collect(Collectors.toUnmodifiableSet());
    }

    public Set<String> blockedAccountSet() {
        return blockedAccounts.stream()
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toUnmodifiableSet());
    }
}
