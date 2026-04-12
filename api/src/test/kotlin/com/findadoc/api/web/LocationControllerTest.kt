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
class LocationControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll returns regions sorted with nested cities`() {
        mockMvc.get("/api/v1/locations")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(2) }
                jsonPath("$.items[0].slug") { value("tbilisi") }
                jsonPath("$.items[1].slug") { value("imereti") }
                jsonPath("$.items[1].cities.length()") { value(1) }
                jsonPath("$.items[1].cities[0].slug") { value("kutaisi") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll counts region as sum of its cities`() {
        mockMvc.get("/api/v1/locations")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='tbilisi')].doctorCount") { value(1) }
                jsonPath("$.items[?(@.slug=='imereti')].doctorCount") { value(1) }
                jsonPath("$.items[?(@.slug=='imereti')].cities[0].doctorCount") { value(1) }
            }
    }
}
