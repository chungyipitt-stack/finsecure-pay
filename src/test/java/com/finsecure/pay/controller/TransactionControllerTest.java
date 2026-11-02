package com.finsecure.pay.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.Instant;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.finsecure.pay.model.TransactionRequest;
import com.finsecure.pay.model.ValidationResult;
import com.finsecure.pay.model.ValidationStatus;
import com.finsecure.pay.model.Violation;
import com.finsecure.pay.service.TransactionValidationService;

@WebMvcTest(value = TransactionController.class, properties = "finsecure.security.api-key=")
class TransactionControllerTest {

    private static final String BODY = """
            {"transactionId":"TXN-0001","sourceAccount":"1234567890","destinationAccount":"9876543210",
             "amount":100.00,"currency":"SGD"}
            """;

    @Autowired
    private MockMvc mvc;

    @MockitoBean
    private TransactionValidationService service;

    @Test
    void returns200WhenApproved() throws Exception {
        when(service.validate(any(TransactionRequest.class))).thenReturn(
                new ValidationResult("TXN-0001", ValidationStatus.APPROVED, List.of(), Instant.now()));

        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("APPROVED"))
                .andExpect(jsonPath("$.violations").isEmpty());
    }

    @Test
    void returns422WhenRejected() throws Exception {
        when(service.validate(any(TransactionRequest.class))).thenReturn(
                new ValidationResult("TXN-0001", ValidationStatus.REJECTED,
                        List.of(new Violation("AMOUNT_EXCEEDS_LIMIT", "too much")), Instant.now()));

        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.status").value("REJECTED"))
                .andExpect(jsonPath("$.violations[0].code").value("AMOUNT_EXCEEDS_LIMIT"));
    }

    @Test
    void returns400ForMalformedJson() throws Exception {
        mvc.perform(post("/validate").contentType(MediaType.APPLICATION_JSON).content("{not-json"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("MALFORMED_REQUEST"));
    }

    @Test
    void returns415ForWrongContentType() throws Exception {
        mvc.perform(post("/validate").contentType(MediaType.TEXT_PLAIN).content("hello"))
                .andExpect(status().isUnsupportedMediaType());
    }
}
