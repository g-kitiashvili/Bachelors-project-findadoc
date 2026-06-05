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
class MapPinsTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/map-pins-test-fixture.sql")
    fun `map-pins returns all located clinics when no radius given`() {
        mockMvc.get("/api/v1/doctors/map-pins")
            .andExpect {
                status { isOk() }
                jsonPath("$.pins.length()") { value(2) } // no-loc-clinic excluded (null location)
                jsonPath("$.pins[?(@.slug=='near-clinic')]") { isNotEmpty() }
            }
    }

    @Test
    @Sql("/sql/map-pins-test-fixture.sql")
    fun `map-pins clinic filter shows only the selected clinic, not its doctors' other clinics`() {
        // doc-near practices at both near-clinic and far-clinic; filtering by near-clinic must not
        // surface far-clinic just because they share a doctor.
        mockMvc.get("/api/v1/doctors/map-pins") {
            param("clinic", "near-clinic")
        }.andExpect {
            status { isOk() }
            jsonPath("$.pins.length()") { value(1) }
            jsonPath("$.pins[0].slug") { value("near-clinic") }
            jsonPath("$.pins[0].doctorCount") { value(1) }
            jsonPath("$.pins[?(@.slug=='far-clinic')]") { isEmpty() }
        }
    }

    @Test
    @Sql("/sql/map-pins-test-fixture.sql")
    fun `map-pins radius filter keeps only clinics within range`() {
        mockMvc.get("/api/v1/doctors/map-pins") {
            param("center", "41.700,44.800")
            param("radiusKm", "10")
        }.andExpect {
            status { isOk() }
            jsonPath("$.pins.length()") { value(1) }
            jsonPath("$.pins[0].slug") { value("near-clinic") }
            jsonPath("$.pins[0].doctorCount") { value(1) }
        }
    }
}
