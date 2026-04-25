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
class SpecialtyControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll returns specialties sorted by sortOrder then nameEn`() {
        mockMvc.get("/api/v1/specialties")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(6) }
                jsonPath("$.items[0].slug") { value("cardiology") }
                jsonPath("$.items[1].slug") { value("pediatrics") }
                jsonPath("$.items[2].slug") { value("dermatology") }
                jsonPath("$.items[3].slug") { value("surgery") }
                jsonPath("$.items[4].slug") { value("neurology") }
                jsonPath("$.items[5].slug") { value("immunology") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll counts every doctor mapped to a specialty including secondary`() {
        mockMvc.get("/api/v1/specialties")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='cardiology')].doctorCount") { value(2) }
                jsonPath("$.items[?(@.slug=='neurology')].doctorCount") { value(2) }
                jsonPath("$.items[?(@.slug=='pediatrics')].doctorCount") { value(1) }
                jsonPath("$.items[?(@.slug=='dermatology')].doctorCount") { value(1) }
                jsonPath("$.items[?(@.slug=='surgery')].doctorCount") { value(1) }
                jsonPath("$.items[?(@.slug=='immunology')].doctorCount") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getBySlug returns detail with all three stat counts`() {
        mockMvc.get("/api/v1/specialties/cardiology")
            .andExpect {
                status { isOk() }
                jsonPath("$.slug") { value("cardiology") }
                jsonPath("$.nameEn") { value("Cardiology") }
                jsonPath("$.nameKa") { value("კარდიოლოგია") }
                jsonPath("$.doctorCount") { value(2) }
                jsonPath("$.acceptingCount") { value(2) }
                jsonPath("$.treatsChildrenCount") { value(1) }
            }
    }

    @Test
    fun `getBySlug returns 404 for unknown slug`() {
        mockMvc.get("/api/v1/specialties/does-not-exist")
            .andExpect {
                status { isNotFound() }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll scopes doctor counts to the region filter`() {
        mockMvc.get("/api/v1/specialties?region=imereti")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='cardiology')].doctorCount") { value(1) }
            }
        mockMvc.get("/api/v1/specialties?region=tbilisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='cardiology')]") { isEmpty() }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll scopes doctor counts to the city filter`() {
        mockMvc.get("/api/v1/specialties?city=kutaisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='cardiology')].doctorCount") { value(1) }
            }
    }
}
