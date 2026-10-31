package com.finsecure.pay;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.actuate.observability.AutoConfigureObservability;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

/**
 * Boots the full application context and exercises the real endpoints end-to-end.
 */
@SpringBootTest(properties = "finsecure.validation.blocked-accounts=5555555555")
@AutoConfigureMockMvc
@AutoConfigureObservability
class FinSecurePayApplicationTests {

    @Autowired
    private MockMvc mvc;

    @Test
    void healthEndpointReportsUp() throws Exception {
        mvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.service").value("finsecure-pay"))
                .andExpect(jsonPath("$.version").exists());
    }

    @Test
    void kubernetesProbesAreExposed() throws Exception {
        mvc.perform(get("/actuator/health/liveness")).andExpect(status().isOk());
        mvc.perform(get("/actuator/health/readiness")).andExpect(status().isOk());
    }

    @Test
    void validTransactionIsApprovedEndToEnd() throws Exception {
        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content("""
                        {"transactionId":"TXN-E2E-0001","sourceAccount":"1234567890",
                         "destinationAccount":"9876543210","amount":500.00,"currency":"USD"}
                        """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("APPROVED"));
    }

    @Test
    void blockedAccountFromConfigurationIsRejected() throws Exception {
        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content("""
                        {"transactionId":"TXN-E2E-0002","sourceAccount":"5555555555",
                         "destinationAccount":"9876543210","amount":500.00,"currency":"USD"}
                        """))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.violations[0].code").value("SOURCE_ACCOUNT_BLOCKED"));
    }

    @Test
    void prometheusEndpointExposesCustomMetrics() throws Exception {
        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content("""
                {"transactionId":"TXN-E2E-0003","sourceAccount":"1234567890",
                 "destinationAccount":"9876543210","amount":1.00,"currency":"SGD"}
                """));
        mvc.perform(get("/actuator/prometheus"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("finsecure_validations_total")));
    }
}
