package com.finsecure.pay;

import static org.junit.jupiter.api.Assertions.assertFalse;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Evaluation Core Test Case TC02:
 * Passes under normal execution, and fails deterministically when
 * -Dfinsecure.test.simulateFailure=true is passed (or SIMULATE_TEST_FAILURE=true in Jenkins)
 * to demonstrate that a failing unit test halts the Jenkins pipeline and blocks deployment.
 */
class ControlledEvaluationTest {

    @Test
    @DisplayName("TC02 evaluation gate: passes normally, fails when finsecure.test.simulateFailure=true")
    void controlledEvaluationGate() {
        boolean simulateFailure = Boolean.parseBoolean(
                System.getProperty("finsecure.test.simulateFailure", "false"));
        assertFalse(simulateFailure,
                "Controlled failing test triggered for CI/CD evaluation (TC02) - deployment must not proceed");
    }
}
