package com.finsecure.pay.service;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.finsecure.pay.config.ValidationProperties;
import com.finsecure.pay.model.TransactionRequest;
import com.finsecure.pay.model.ValidationResult;
import com.finsecure.pay.model.ValidationStatus;
import com.finsecure.pay.model.Violation;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

/**
 * Applies FinSecure Pay business rules to a transaction.
 *
 * <p>Rules (all are evaluated so the client receives every violation at once):
 * <ol>
 *   <li>transactionId is present and matches {@code TXN-[A-Za-z0-9-]{4,36}}</li>
 *   <li>source / destination accounts are present and 10-12 digits</li>
 *   <li>source and destination accounts differ</li>
 *   <li>amount is present, positive, within [minAmount, maxAmount] and has at most 2 decimals</li>
 *   <li>currency is present and in the supported list</li>
 *   <li>neither account is on the compliance block list</li>
 *   <li>timestamp (if supplied) is not in the future beyond the allowed clock skew</li>
 * </ol>
 */
@Service
public class TransactionValidationService {

    private static final Logger log = LoggerFactory.getLogger(TransactionValidationService.class);

    static final Pattern TXN_ID_PATTERN = Pattern.compile("^TXN-[A-Za-z0-9-]{4,36}$");
    static final Pattern ACCOUNT_PATTERN = Pattern.compile("^\\d{10,12}$");

    private final ValidationProperties props;
    private final Clock clock;
    private final MeterRegistry meterRegistry;
    private final Timer validationTimer;
    private final Set<String> supportedCurrencies;
    private final Set<String> blockedAccounts;

    public TransactionValidationService(ValidationProperties props, Clock clock, MeterRegistry meterRegistry) {
        this.props = props;
        this.clock = clock;
        this.meterRegistry = meterRegistry;
        this.supportedCurrencies = props.supportedCurrencySet();
        this.blockedAccounts = props.blockedAccountSet();
        this.validationTimer = Timer.builder("finsecure.validation.duration")
                .description("Time taken to validate a transaction")
                .publishPercentileHistogram()
                .register(meterRegistry);
    }

    public ValidationResult validate(TransactionRequest request) {
        return validationTimer.record(() -> doValidate(request));
    }

    private ValidationResult doValidate(TransactionRequest req) {
        List<Violation> violations = new ArrayList<>();

        validateTransactionId(req.transactionId(), violations);
        validateAccounts(req.sourceAccount(), req.destinationAccount(), violations);
        validateAmount(req.amount(), violations);
        validateCurrency(req.currency(), violations);
        validateTimestamp(req.timestamp(), violations);

        ValidationStatus status = violations.isEmpty() ? ValidationStatus.APPROVED : ValidationStatus.REJECTED;
        recordMetrics(status, violations);

        if (status == ValidationStatus.APPROVED) {
            log.info("Transaction {} APPROVED amount={} {}", req.transactionId(), req.amount(), req.currency());
        } else {
            log.warn("Transaction {} REJECTED violations={}", req.transactionId(),
                    violations.stream().map(Violation::code).toList());
        }
        return new ValidationResult(req.transactionId(), status, List.copyOf(violations), Instant.now(clock));
    }

    private void validateTransactionId(String id, List<Violation> v) {
        if (isBlank(id)) {
            v.add(new Violation("TRANSACTION_ID_REQUIRED", "transactionId is required"));
        } else if (!TXN_ID_PATTERN.matcher(id).matches()) {
            v.add(new Violation("TRANSACTION_ID_INVALID",
                    "transactionId must match TXN-<4-36 alphanumeric characters or hyphens>"));
        }
    }

    private void validateAccounts(String source, String destination, List<Violation> v) {
        boolean sourceOk = validateAccount("SOURCE", "sourceAccount", source, v);
        boolean destOk = validateAccount("DESTINATION", "destinationAccount", destination, v);

        if (sourceOk && destOk && source.equals(destination)) {
            v.add(new Violation("SAME_ACCOUNT", "sourceAccount and destinationAccount must be different"));
        }
        if (sourceOk && blockedAccounts.contains(source)) {
            v.add(new Violation("SOURCE_ACCOUNT_BLOCKED", "sourceAccount is blocked by compliance"));
        }
        if (destOk && blockedAccounts.contains(destination)) {
            v.add(new Violation("DESTINATION_ACCOUNT_BLOCKED", "destinationAccount is blocked by compliance"));
        }
    }

    private boolean validateAccount(String prefix, String field, String value, List<Violation> v) {
        if (isBlank(value)) {
            v.add(new Violation(prefix + "_ACCOUNT_REQUIRED", field + " is required"));
            return false;
        }
        if (!ACCOUNT_PATTERN.matcher(value).matches()) {
            v.add(new Violation(prefix + "_ACCOUNT_INVALID", field + " must be 10-12 digits"));
            return false;
        }
        return true;
    }

    private void validateAmount(BigDecimal amount, List<Violation> v) {
        if (amount == null) {
            v.add(new Violation("AMOUNT_REQUIRED", "amount is required"));
            return;
        }
        if (amount.signum() <= 0) {
            v.add(new Violation("AMOUNT_NOT_POSITIVE", "amount must be greater than zero"));
            return;
        }
        if (amount.stripTrailingZeros().scale() > 2) {
            v.add(new Violation("AMOUNT_INVALID_PRECISION", "amount must have at most 2 decimal places"));
        }
        if (amount.compareTo(props.minAmount()) < 0) {
            v.add(new Violation("AMOUNT_BELOW_MINIMUM",
                    "amount " + amount.toPlainString() + " is below minimum " + props.minAmount().toPlainString()));
        }
        if (amount.compareTo(props.maxAmount()) > 0) {
            v.add(new Violation("AMOUNT_EXCEEDS_LIMIT",
                    "amount " + amount.toPlainString() + " exceeds limit " + props.maxAmount().toPlainString()));
        }
    }

    private void validateCurrency(String currency, List<Violation> v) {
        if (isBlank(currency)) {
            v.add(new Violation("CURRENCY_REQUIRED", "currency is required"));
        } else if (!supportedCurrencies.contains(currency.trim().toUpperCase())) {
            v.add(new Violation("CURRENCY_UNSUPPORTED",
                    "currency " + currency + " is not supported; allowed: " + supportedCurrencies));
        }
    }

    private void validateTimestamp(Instant timestamp, List<Violation> v) {
        if (timestamp == null) {
            return; // optional
        }
        Instant latestAllowed = Instant.now(clock).plusSeconds(props.maxFutureSkewSeconds());
        if (timestamp.isAfter(latestAllowed)) {
            v.add(new Violation("TIMESTAMP_IN_FUTURE", "timestamp must not be in the future"));
        }
    }

    private void recordMetrics(ValidationStatus status, List<Violation> violations) {
        Counter.builder("finsecure.validations")
                .description("Number of transaction validations by result")
                .tag("result", status.name().toLowerCase())
                .register(meterRegistry)
                .increment();
        for (Violation violation : violations) {
            Counter.builder("finsecure.validation.violations")
                    .description("Number of rule violations by rule code")
                    .tag("code", violation.code())
                    .register(meterRegistry)
                    .increment();
        }
    }

    private static boolean isBlank(String s) {
        return s == null || s.isBlank();
    }
}
