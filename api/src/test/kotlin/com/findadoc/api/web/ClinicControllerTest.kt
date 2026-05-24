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
class ClinicControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getAll returns clinics with doctor counts`() {
        mockMvc.get("/api/v1/clinics")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='alpha-clinic')].doctorCount") { value(1) }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getAll excludes clinics with no doctors`() {
        mockMvc.get("/api/v1/clinics")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='beta-clinic')]") { isEmpty() }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getBySlug returns clinic detail`() {
        mockMvc.get("/api/v1/clinics/alpha-clinic")
            .andExpect {
                status { isOk() }
                jsonPath("$.nameEn") { value("Alpha Clinic") }
                jsonPath("$.doctorCount") { value(1) }
            }
    }

    @Test
    fun `getBySlug returns 404 for unknown slug`() {
        mockMvc.get("/api/v1/clinics/does-not-exist")
            .andExpect {
                status { isNotFound() }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getAll q matches clinic by name`() {
        mockMvc.get("/api/v1/clinics?q=alpha")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='alpha-clinic')].doctorCount") { value(1) }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getAll returns a paginated envelope`() {
        mockMvc.get("/api/v1/clinics") { param("pageSize", "1") }
            .andExpect {
                status { isOk() }
                jsonPath("$.page") { value(1) }
                jsonPath("$.pageSize") { value(1) }
                jsonPath("$.total") { exists() }
                jsonPath("$.items.length()") { value(org.hamcrest.Matchers.lessThanOrEqualTo(1)) }
            }
    }
}
