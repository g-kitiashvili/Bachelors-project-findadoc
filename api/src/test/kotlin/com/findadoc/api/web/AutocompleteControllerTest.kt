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
class AutocompleteControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions matches doctor by latin name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "Giorgi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors[?(@.slug=='giorgi-tsintsadze')].fullNameEn") { value("Giorgi Tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions matches doctor by georgian name substring`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "ცინცა") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors[?(@.slug=='giorgi-tsintsadze')].fullNameEn") { value("Giorgi Tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions matches specialty by english name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "cardio") }
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties[?(@.slug=='cardiology')].nameEn") { value("Cardiology") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions matches specialty by georgian name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "კარდი") }
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties[?(@.slug=='cardiology')].nameEn") { value("Cardiology") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions returns both groups for a specialty term`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "kardio") }
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties[?(@.slug=='cardiology')].nameEn") { value("Cardiology") }
                jsonPath("$.doctors[?(@.slug=='giorgi-tsintsadze')].fullNameEn") { value("Giorgi Tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions tolerates a typo in the name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "Giorggi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors[?(@.slug=='giorgi-tsintsadze')].fullNameEn") { value("Giorgi Tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions caps each group at five`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "ia") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors.length()") { value(org.hamcrest.Matchers.lessThanOrEqualTo(5)) }
                jsonPath("$.specialties.length()") { value(org.hamcrest.Matchers.lessThanOrEqualTo(5)) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions returns empty groups for blank query`() {
        mockMvc.get("/api/v1/autocomplete")
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors.length()") { value(0) }
                jsonPath("$.specialties.length()") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions returns empty groups for single character`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "k") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors.length()") { value(0) }
                jsonPath("$.specialties.length()") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions returns empty groups below threshold`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "zzzzqqqq") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors.length()") { value(0) }
                jsonPath("$.specialties.length()") { value(0) }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    @Sql("/sql/clinics-test-fixture.sql")
    fun `getSuggestions matches clinic by english name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "alpha") }
            .andExpect {
                status { isOk() }
                jsonPath("$.clinics[?(@.slug=='alpha-clinic')]") { exists() }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getSuggestions doctor shape carries slug and english name`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "Giorgi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.doctors[0].slug") { exists() }
                jsonPath("$.doctors[0].fullNameEn") { exists() }
            }
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `getSuggestions surfaces a specialty via a lay alias with a doctor count`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "heart") }
            .andExpect {
                status { isOk() }
                jsonPath("$.specialties[?(@.slug=='cardiology')].nameEn") { value("Cardiology") }
                jsonPath("$.specialties[?(@.slug=='cardiology')].doctorCount") { value(2) }
            }
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `getSuggestions surfaces a condition via a synonym in its own group`() {
        mockMvc.get("/api/v1/autocomplete") { param("q", "high blood pressure") }
            .andExpect {
                status { isOk() }
                jsonPath("$.conditions[?(@.slug=='hypertension')].nameEn") { value("Hypertension") }
                jsonPath("$.conditions[?(@.slug=='hypertension')].doctorCount") { value(2) }
            }
    }
}
