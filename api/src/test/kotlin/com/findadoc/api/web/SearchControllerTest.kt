package com.findadoc.api.web

import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.jdbc.Sql
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get
import org.springframework.transaction.annotation.Transactional

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class SearchControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve routes a lay term to a specialty`() {
        mockMvc.get("/api/v1/search/resolve") { param("q", "heart") }
            .andExpect {
                status { isOk() }
                jsonPath("$.type") { value("specialty") }
                jsonPath("$.slug") { value("cardiology") }
                jsonPath("$.label") { value("Cardiology") }
            }
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve routes a synonym to a condition`() {
        mockMvc.get("/api/v1/search/resolve") { param("q", "high blood pressure") }
            .andExpect {
                status { isOk() }
                jsonPath("$.type") { value("condition") }
                jsonPath("$.slug") { value("hypertension") }
            }
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve falls back to query when nothing matches`() {
        mockMvc.get("/api/v1/search/resolve") { param("q", "zzzzqqqq") }
            .andExpect {
                status { isOk() }
                jsonPath("$.type") { value("query") }
                jsonPath("$.slug") { value(null) }
                jsonPath("$.label") { value("zzzzqqqq") }
            }
    }

    @Test
    fun `resolve returns query fallback for blank input`() {
        mockMvc.get("/api/v1/search/resolve")
            .andExpect {
                status { isOk() }
                jsonPath("$.type") { value("query") }
            }
    }
}
