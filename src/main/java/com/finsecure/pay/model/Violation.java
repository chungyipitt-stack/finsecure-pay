package com.finsecure.pay.model;

/**
 * A single validation-rule violation.
 *
 * @param code    stable machine-readable rule code (e.g. AMOUNT_EXCEEDS_LIMIT)
 * @param message human-readable explanation
 */
public record Violation(String code, String message) {
}
