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
class DoctorListTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql(value = ["/sql/cleanup.sql"], executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
    fun `getAll returns empty page when no doctors`() {
        mockMvc.get("/api/v1/doctors")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(0) }
                jsonPath("$.total") { value(0) }
                jsonPath("$.page") { value(1) }
                jsonPath("$.pageSize") { value(5) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll returns first page with default pageSize 5`() {
        mockMvc.get("/api/v1/doctors")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(5) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(1) }
                jsonPath("$.pageSize") { value(5) }
                jsonPath("$.items[0].slug") { value("a-test") }
                jsonPath("$.items[4].slug") { value("e-test") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll page=2 returns remaining 2 doctors`() {
        mockMvc.get("/api/v1/doctors?page=2")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(2) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(2) }
                jsonPath("$.items[0].slug") { value("f-test") }
                jsonPath("$.items[1].slug") { value("g-test") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll page=999 returns empty items with correct total`() {
        mockMvc.get("/api/v1/doctors?page=999")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(0) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(999) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll pageSize over max clamps to 50`() {
        mockMvc.get("/api/v1/doctors?pageSize=1000")
            .andExpect {
                status { isOk() }
                jsonPath("$.pageSize") { value(50) }
                jsonPath("$.items.length()") { value(7) }
                jsonPath("$.total") { value(7) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll excludes INACTIVE doctors`() {
        mockMvc.get("/api/v1/doctors?pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[?(@.slug == 'inactive-test')]") { isEmpty() }
            }
    }
}
