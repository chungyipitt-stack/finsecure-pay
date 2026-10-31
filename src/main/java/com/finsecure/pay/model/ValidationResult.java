package com.finsecure.pay.model;

import java.time.Instant;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnore;

/**
 * Outcome of validating a {@link TransactionRequest}.
 *
 * @param transactionId echoed transaction id (may be null if it was missing)
 * @param status        APPROVED or REJECTED
 * @param violations    list of rule violations (empty when APPROVED)
 * @param validatedAt   server time of validation
 */
public record ValidationResult(
        String transactionId,
        ValidationStatus status,
        List<Violation> violations,
        Instant validatedAt) {

    @JsonIgnore
    public boolean isApproved() {
        return status == ValidationStatus.APPROVED;
    }
}
