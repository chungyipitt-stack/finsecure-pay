package com.finsecure.pay.model;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Incoming transaction to be validated.
 *
 * @param transactionId      client-generated unique id (e.g. TXN-20261031-0001)
 * @param sourceAccount      debit account number (10-12 digits)
 * @param destinationAccount credit account number (10-12 digits)
 * @param amount             positive amount with at most 2 decimal places
 * @param currency           ISO-4217 currency code
 * @param timestamp          time the transaction was initiated (optional)
 */
public record TransactionRequest(
        String transactionId,
        String sourceAccount,
        String destinationAccount,
        BigDecimal amount,
        String currency,
        Instant timestamp) {
}
