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
class MedicalConditionControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql("/sql/conditions-test-fixture.sql")
    fun `getAll returns conditions sorted by sortOrder then nameEn`() {
        mockMvc.get("/api/v1/conditions")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(2) }
                jsonPath("$.items[0].slug") { value("hypertension") }
                jsonPath("$.items[1].slug") { value("migraine") }
            }
    }

    @Test
    @Sql("/sql/conditions-test-fixture.sql")
    fun `getAll counts distinct active doctors through the mapped specialty`() {
        mockMvc.get("/api/v1/conditions")
            .andExpect {
                status { isOk() }
                jsonPath("$.items[?(@.slug=='hypertension')].doctorCount") { value(2) }
                jsonPath("$.items[?(@.slug=='migraine')].doctorCount") { value(0) }
            }
    }

    @Test
    @Sql("/sql/conditions-test-fixture.sql")
    fun `getBySlug returns detail with all three stat counts`() {
        mockMvc.get("/api/v1/conditions/hypertension")
            .andExpect {
                status { isOk() }
                jsonPath("$.slug") { value("hypertension") }
                jsonPath("$.nameEn") { value("Hypertension") }
                jsonPath("$.nameKa") { value("არტერიული ჰიპერტენზია") }
                jsonPath("$.doctorCount") { value(2) }
                jsonPath("$.acceptingCount") { value(1) }
                jsonPath("$.treatsChildrenCount") { value(1) }
            }
    }

    @Test
    fun `getBySlug returns 404 for unknown slug`() {
        mockMvc.get("/api/v1/conditions/does-not-exist")
            .andExpect {
                status { isNotFound() }
            }
    }
}
