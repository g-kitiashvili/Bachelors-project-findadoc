package com.findadoc.api.web

import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get

@SpringBootTest
@AutoConfigureMockMvc
class OpenApiDocsTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    fun `openApi exposes configured title in spec`() {
        mockMvc.get("/v3/api-docs")
            .andExpect {
                status { isOk() }
                jsonPath("$.info.title") { value("Find-a-Doc API") }
            }
    }

    @Test
    fun `getBySlug is documented under Doctors tag with summary`() {
        mockMvc.get("/v3/api-docs")
            .andExpect {
                status { isOk() }
                jsonPath("$.paths./api/v1/doctors/{slug}.get.tags[0]") { value("Doctors") }
                jsonPath("$.paths./api/v1/doctors/{slug}.get.summary") { value("Get a doctor by slug") }
            }
    }
}
