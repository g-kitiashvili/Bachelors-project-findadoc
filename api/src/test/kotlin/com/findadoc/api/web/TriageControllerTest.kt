package com.findadoc.api.web

import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get

@SpringBootTest
@AutoConfigureMockMvc
class TriageControllerTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    fun `GET triage returns the graph`() {
        mockMvc.get("/api/v1/triage").andExpect {
            status { isOk() }
            jsonPath("$.start") { exists() }
            jsonPath("$.nodes['q_area'].options[0].label.en") { exists() }
        }
    }
}
