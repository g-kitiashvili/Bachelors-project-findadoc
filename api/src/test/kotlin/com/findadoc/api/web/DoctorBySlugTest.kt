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
        mockMvc.get("/api/v1/doctors/giorgi-tsintsadze")
            .andExpect {
                status { isOk() }
                jsonPath("$.slug") { value("giorgi-tsintsadze") }
                jsonPath("$.fullNameKa") { value("გიორგი ცინცაძე") }
                jsonPath("$.fullNameEn") { value("Giorgi Tsintsadze") }
                jsonPath("$.specialtyKa") { value("კარდიოლოგი") }
                jsonPath("$.specialtyEn") { value("Cardiologist") }
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

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getBySlug returns specialties array with primary first`() {
        mockMvc.get("/api/v1/doctors/luka-javakhishvili")
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties.length()") { value(2) }
                jsonPath("$.specialties[0].slug") { value("dermatology") }
                jsonPath("$.specialties[0].isPrimary") { value(true) }
                jsonPath("$.specialties[1].slug") { value("neurology") }
                jsonPath("$.specialties[1].isPrimary") { value(false) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getBySlug returns empty specialties array when doctor has no mapping`() {
        mockMvc.get("/api/v1/doctors/ana-eradze")
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties.length()") { value(0) }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getBySlug returns clinics array for a doctor with a clinic`() {
        mockMvc.get("/api/v1/doctors/doc-kutaisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.clinics") { isArray() }
                jsonPath("$.clinics.length()") { value(1) }
                jsonPath("$.clinics[0].slug") { value("alpha-clinic") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getBySlug returns empty clinics array when doctor has no clinic`() {
        mockMvc.get("/api/v1/doctors/doc-tbilisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.clinics") { isArray() }
                jsonPath("$.clinics.length()") { value(0) }
            }
    }
}
