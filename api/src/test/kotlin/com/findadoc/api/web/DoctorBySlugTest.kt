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
class DoctorBySlugTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getBySlug returns 200 with full profile when slug found`() {
        mockMvc.get("/api/v1/doctors/a-test")
            .andExpect {
                status { isOk() }
                jsonPath("$.slug") { value("a-test") }
                jsonPath("$.fullNameKa") { value("ა ტესტი") }
                jsonPath("$.fullNameEn") { value("A Test") }
                jsonPath("$.gender") { isEmpty() }
                jsonPath("$.photoUrl") { isEmpty() }
                jsonPath("$.isAcceptingNewPatients") { value(true) }
                jsonPath("$.treatsChildren") { value(false) }
                jsonPath("$.treatsAdults") { value(true) }
                jsonPath("$.bioKa") { isEmpty() }
                jsonPath("$.bioEn") { isEmpty() }
            }
    }

    @Test
    fun `getBySlug returns 404 problem+json when slug not found`() {
        mockMvc.get("/api/v1/doctors/does-not-exist")
            .andExpect {
                status { isNotFound() }
                content { contentType("application/problem+json") }
                jsonPath("$.type") { value("https://findadoc.example.com/problems/doctor-not-found") }
                jsonPath("$.title") { value("Doctor not found") }
                jsonPath("$.status") { value(404) }
                jsonPath("$.detail") { value("Doctor with slug 'does-not-exist' not found") }
                jsonPath("$.slug") { value("does-not-exist") }
            }
    }
}
