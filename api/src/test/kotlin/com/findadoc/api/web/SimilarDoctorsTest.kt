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
class SimilarDoctorsTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/similar-doctors-test-fixture.sql")
    fun `similar returns same-specialty peers, same-city first, excluding self, other specialties, and merged`() {
        mockMvc.get("/api/v1/doctors/sim-target/similar")
            .andExpect {
                status { isOk() }
                jsonPath("$.length()") { value(2) }
                jsonPath("$[0].slug") { value("sim-samecity") }   // shared specialty + same city ranks first
                jsonPath("$[1].slug") { value("sim-othercity") }  // shared specialty, different city
                jsonPath("$[?(@.slug=='sim-target')]") { isEmpty() }   // self excluded
                jsonPath("$[?(@.slug=='sim-derm')]") { isEmpty() }     // no shared specialty
                jsonPath("$[?(@.slug=='sim-merged')]") { isEmpty() }   // merged row excluded
            }
    }

    @Test
    @Sql("/sql/similar-doctors-test-fixture.sql")
    fun `similar respects the limit parameter`() {
        mockMvc.get("/api/v1/doctors/sim-target/similar?limit=1")
            .andExpect {
                status { isOk() }
                jsonPath("$.length()") { value(1) }
                jsonPath("$[0].slug") { value("sim-samecity") }
            }
    }
}
