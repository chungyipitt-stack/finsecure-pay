package com.finsecure.pay.config;

import java.time.Clock;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    /** Injectable clock so time-based rules can be unit tested deterministically. */
    @Bean
    public Clock clock() {
        return Clock.systemUTC();
    }
}
