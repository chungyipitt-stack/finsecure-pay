package com.finsecure.pay.service;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import com.finsecure.pay.config.ValidationProperties;
import com.finsecure.pay.model.TransactionRequest;
import com.finsecure.pay.model.ValidationResult;
import com.finsecure.pay.model.ValidationStatus;
import com.finsecure.pay.model.Violation;

import io.micrometer.core.instrument.simple.SimpleMeterRegistry;

@DisplayName("TransactionValidationService")
class TransactionValidationServiceTest {

    private static final Instant NOW = Instant.parse("2026-10-31T12:00:00Z");
    private static final String SRC = "1234567890";
    private static final String DST = "9876543210";
    private static final String BLOCKED = "1111111111";

    private TransactionValidationService service;
    private SimpleMeterRegistry registry;

    @BeforeEach
    void setUp() {
        ValidationProperties props = new ValidationProperties(
                new BigDecimal("10000.00"),
                new BigDecimal("0.01"),
                List.of("SGD", "USD", "EUR", "MYR"),
                List.of(BLOCKED),
                300);
        registry = new SimpleMeterRegistry();
        service = new TransactionValidationService(props, Clock.fixed(NOW, ZoneOffset.UTC), registry);
    }

    private static TransactionRequest valid() {
        return new TransactionRequest("TXN-20261031-0001", SRC, DST, new BigDecimal("250.00"), "SGD", NOW);
    }

    private static TransactionRequest withAmount(String amount) {
        return new TransactionRequest("TXN-20261031-0001", SRC, DST,
                amount == null ? null : new BigDecimal(amount), "SGD", NOW);
    }

    private static List<String> codes(ValidationResult r) {
        return r.violations().stream().map(Violation::code).toList();
    }

    @Nested
    @DisplayName("successful validation")
    class Success {

        @Test
        @DisplayName("approves a well-formed transaction")
        void approvesValidTransaction() {
            ValidationResult result = service.validate(valid());

            assertThat(result.status()).isEqualTo(ValidationStatus.APPROVED);
            assertThat(result.violations()).isEmpty();
            assertThat(result.transactionId()).isEqualTo("TXN-20261031-0001");
            assertThat(result.validatedAt()).isEqualTo(NOW);
        }

        @Test
        @DisplayName("approves amount exactly at the maximum limit")
        void approvesAtLimit() {
            assertThat(service.validate(withAmount("10000.00")).isApproved()).isTrue();
        }

        @Test
        @DisplayName("approves amount exactly at the minimum")
        void approvesAtMinimum() {
            assertThat(service.validate(withAmount("0.01")).isApproved()).isTrue();
        }

        @Test
        @DisplayName("accepts lower-case currency codes")
        void acceptsLowerCaseCurrency() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, "usd", null);
            assertThat(service.validate(req).isApproved()).isTrue();
        }

        @Test
        @DisplayName("treats timestamp as optional")
        void timestampOptional() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, "SGD", null);
            assertThat(service.validate(req).isApproved()).isTrue();
        }
    }

    @Nested
    @DisplayName("amount rules")
    class AmountRules {

        @Test
        void rejectsMissingAmount() {
            assertThat(codes(service.validate(withAmount(null)))).containsExactly("AMOUNT_REQUIRED");
        }

        @ParameterizedTest
        @ValueSource(strings = {"0", "0.00", "-1", "-250.50"})
        void rejectsZeroOrNegative(String amount) {
            assertThat(codes(service.validate(withAmount(amount)))).containsExactly("AMOUNT_NOT_POSITIVE");
        }

        @Test
        void rejectsAmountAboveLimit() {
            ValidationResult r = service.validate(withAmount("10000.01"));
            assertThat(r.status()).isEqualTo(ValidationStatus.REJECTED);
            assertThat(codes(r)).containsExactly("AMOUNT_EXCEEDS_LIMIT");
        }

        @Test
        void rejectsMoreThanTwoDecimals() {
            assertThat(codes(service.validate(withAmount("10.123")))).contains("AMOUNT_INVALID_PRECISION");
        }

        @Test
        void rejectsBelowMinimum() {
            assertThat(codes(service.validate(withAmount("0.001"))))
                    .contains("AMOUNT_BELOW_MINIMUM", "AMOUNT_INVALID_PRECISION");
        }
    }

    @Nested
    @DisplayName("account rules")
    class AccountRules {

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   "})
        void rejectsMissingSource(String source) {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", source, DST, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("SOURCE_ACCOUNT_REQUIRED");
        }

        @ParameterizedTest
        @ValueSource(strings = {"123", "1234567890123", "12345abcde", "12-3456789"})
        void rejectsMalformedDestination(String dest) {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, dest, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("DESTINATION_ACCOUNT_INVALID");
        }

        @Test
        void rejectsSameSourceAndDestination() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, SRC, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("SAME_ACCOUNT");
        }

        @Test
        void rejectsBlockedSourceAccount() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", BLOCKED, DST, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("SOURCE_ACCOUNT_BLOCKED");
        }

        @Test
        void rejectsBlockedDestinationAccount() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, BLOCKED, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("DESTINATION_ACCOUNT_BLOCKED");
        }
    }

    @Nested
    @DisplayName("identifier, currency and timestamp rules")
    class OtherRules {

        @Test
        void rejectsMissingTransactionId() {
            TransactionRequest req = new TransactionRequest(null, SRC, DST, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("TRANSACTION_ID_REQUIRED");
        }

        @ParameterizedTest
        @ValueSource(strings = {"12345", "TXN-", "TXN-AB", "txn-ABCD", "TXN-ABCD!"})
        void rejectsMalformedTransactionId(String id) {
            TransactionRequest req = new TransactionRequest(id, SRC, DST, BigDecimal.TEN, "SGD", null);
            assertThat(codes(service.validate(req))).containsExactly("TRANSACTION_ID_INVALID");
        }

        @Test
        void rejectsMissingCurrency() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, null, null);
            assertThat(codes(service.validate(req))).containsExactly("CURRENCY_REQUIRED");
        }

        @Test
        void rejectsUnsupportedCurrency() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, "JPY", null);
            assertThat(codes(service.validate(req))).containsExactly("CURRENCY_UNSUPPORTED");
        }

        @Test
        void rejectsFutureTimestampBeyondSkew() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, "SGD",
                    NOW.plusSeconds(301));
            assertThat(codes(service.validate(req))).containsExactly("TIMESTAMP_IN_FUTURE");
        }

        @Test
        void allowsFutureTimestampWithinSkew() {
            TransactionRequest req = new TransactionRequest("TXN-ABCD", SRC, DST, BigDecimal.TEN, "SGD",
                    NOW.plusSeconds(299));
            assertThat(service.validate(req).isApproved()).isTrue();
        }
    }

    @Test
    @DisplayName("reports every violation at once")
    void reportsAllViolations() {
        TransactionRequest req = new TransactionRequest("bad", "abc", "abc", new BigDecimal("-5"), "XYZ", null);
        assertThat(codes(service.validate(req))).containsExactlyInAnyOrder(
                "TRANSACTION_ID_INVALID", "SOURCE_ACCOUNT_INVALID", "DESTINATION_ACCOUNT_INVALID",
                "AMOUNT_NOT_POSITIVE", "CURRENCY_UNSUPPORTED");
    }

    @Test
    @DisplayName("records approved/rejected metrics")
    void recordsMetrics() {
        service.validate(valid());
        service.validate(withAmount("99999"));

        assertThat(registry.counter("finsecure.validations", "result", "approved").count()).isEqualTo(1.0);
        assertThat(registry.counter("finsecure.validations", "result", "rejected").count()).isEqualTo(1.0);
        assertThat(registry.counter("finsecure.validation.violations", "code", "AMOUNT_EXCEEDS_LIMIT").count())
                .isEqualTo(1.0);
        assertThat(registry.timer("finsecure.validation.duration").count()).isEqualTo(2);
    }
}
