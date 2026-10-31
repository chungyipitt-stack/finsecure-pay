package com.finsecure.pay.security;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class ApiKeyFilterTest {

    private static MockHttpServletRequest request(String uri, String key) {
        MockHttpServletRequest req = new MockHttpServletRequest("POST", uri);
        if (key != null) {
            req.addHeader(ApiKeyFilter.HEADER, key);
        }
        return req;
    }

    @Test
    void allowsValidKey() throws Exception {
        MockHttpServletResponse res = new MockHttpServletResponse();
        MockFilterChain chain = new MockFilterChain();
        new ApiKeyFilter("s3cret").doFilter(request("/validate", "s3cret"), res, chain);

        assertThat(res.getStatus()).isEqualTo(200);
        assertThat(chain.getRequest()).isNotNull();
    }

    @Test
    void rejectsMissingKey() throws Exception {
        MockHttpServletResponse res = new MockHttpServletResponse();
        MockFilterChain chain = new MockFilterChain();
        new ApiKeyFilter("s3cret").doFilter(request("/validate", null), res, chain);

        assertThat(res.getStatus()).isEqualTo(401);
        assertThat(chain.getRequest()).isNull();
    }

    @Test
    void rejectsWrongKey() throws Exception {
        MockHttpServletResponse res = new MockHttpServletResponse();
        new ApiKeyFilter("s3cret").doFilter(request("/validate", "guess"), res, new MockFilterChain());
        assertThat(res.getStatus()).isEqualTo(401);
    }

    @Test
    void doesNotProtectHealth() throws Exception {
        MockHttpServletResponse res = new MockHttpServletResponse();
        MockFilterChain chain = new MockFilterChain();
        new ApiKeyFilter("s3cret").doFilter(request("/health", null), res, chain);
        assertThat(chain.getRequest()).isNotNull();
    }

    @Test
    void disabledWhenNoKeyConfigured() throws Exception {
        MockHttpServletResponse res = new MockHttpServletResponse();
        MockFilterChain chain = new MockFilterChain();
        new ApiKeyFilter("").doFilter(request("/validate", null), res, chain);
        assertThat(chain.getRequest()).isNotNull();
    }
}
