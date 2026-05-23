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
class DedupVisibilityTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/dedup-test-fixture.sql")
    fun `merged clinic is excluded from the clinic list`() {
        mockMvc.get("/api/v1/clinics")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='alpha-merged')]") { doesNotExist() }
                jsonPath("$.items[?(@.slug=='alpha-canonical')]") { exists() }
            }
    }

    @Test
    @Sql("/sql/dedup-test-fixture.sql")
    fun `merged doctor is excluded from the doctor list`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Canon") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='merged-doc')]") { doesNotExist() }
            }
    }

    @Test
    @Sql("/sql/dedup-test-fixture.sql")
    fun `merged doctor slug redirects to the canonical`() {
        mockMvc.get("/api/v1/doctors/merged-doc")
            .andExpect {
                status { isEqualTo(301) }
                header { string("Location", "/api/v1/doctors/canon-doc") }
            }
    }
}
