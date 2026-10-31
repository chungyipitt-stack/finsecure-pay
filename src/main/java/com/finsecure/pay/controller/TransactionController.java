package com.finsecure.pay.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.finsecure.pay.model.TransactionRequest;
import com.finsecure.pay.model.ValidationResult;
import com.finsecure.pay.service.TransactionValidationService;

/**
 * POST /validate - validates a transaction.
 * <ul>
 *   <li>200 OK with status APPROVED when every rule passes</li>
 *   <li>422 Unprocessable Entity with status REJECTED and the list of violations otherwise</li>
 *   <li>400 Bad Request when the body is not valid JSON</li>
 * </ul>
 */
@RestController
public class TransactionController {

    private final TransactionValidationService validationService;

    public TransactionController(TransactionValidationService validationService) {
        this.validationService = validationService;
    }

    @PostMapping(path = "/validate",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ValidationResult> validate(@RequestBody TransactionRequest request) {
        ValidationResult result = validationService.validate(request);
        HttpStatus status = result.isApproved() ? HttpStatus.OK : HttpStatus.UNPROCESSABLE_ENTITY;
        return ResponseEntity.status(status).body(result);
    }
}
