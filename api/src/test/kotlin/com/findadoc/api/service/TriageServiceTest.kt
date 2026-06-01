package com.findadoc.api.service

import com.findadoc.api.web.dto.LocalizedTextDto
import com.findadoc.api.web.dto.TriageGraphDto
import com.findadoc.api.web.dto.TriageNodeDto
import com.findadoc.api.web.dto.TriageOptionDto
import com.findadoc.api.web.dto.TriageResultDto
import com.findadoc.api.web.dto.TriageSymptomDto
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import kotlin.test.assertEquals

class TriageServiceTest {
    private fun lt(s: String) = LocalizedTextDto(s, s)
    private fun result(slug: String) = TriageResultDto("specialty", slug)

    @Test
    fun `validateStructure accepts a valid graph`() {
        val g = TriageGraphDto(
            start = "a",
            nodes = mapOf(
                "a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "b"))),
                "b" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), result = result("cardiology")))),
            ),
        )
        TriageService.validateStructure(g)
    }

    @Test
    fun `validateStructure rejects a missing start node`() {
        val g = TriageGraphDto("missing", mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), result = result("cardiology"))))))
        val e = assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
        assertEquals(true, e.message!!.contains("start"))
    }

    @Test
    fun `validateStructure rejects an option with neither next nor result`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"))))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects an option with both next and result`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "a", result = result("cardiology"))))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a dangling next reference`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "ghost")))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a cycle`() {
        val g = TriageGraphDto(
            start = "a",
            nodes = mapOf(
                "a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "b"))),
                "b" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "a"))),
            ),
        )
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects an unknown result type`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), result = TriageResultDto("treatment", "x"))))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    private fun symptom(slug: String, w: Int = 1) =
        TriageSymptomDto(lt("s"), mapOf("specialty:$slug" to w))

    @Test
    fun `validateStructure accepts a symptom node with weights`() {
        val g = TriageGraphDto(
            start = "a",
            nodes = mapOf(
                "a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), next = "s"))),
                "s" to TriageNodeDto(lt("q"), symptoms = listOf(symptom("cardiology"), symptom("neurology"))),
            ),
        )
        TriageService.validateStructure(g)
    }

    @Test
    fun `validateStructure rejects a node with both options and symptoms`() {
        val g = TriageGraphDto(
            "a",
            mapOf("a" to TriageNodeDto(lt("q"), listOf(TriageOptionDto(lt("o"), result = result("cardiology"))), symptoms = listOf(symptom("neurology")))),
        )
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a node with neither options nor symptoms`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a symptom with no weights`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), symptoms = listOf(TriageSymptomDto(lt("s"), emptyMap())))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a weight key with a bad type`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), symptoms = listOf(TriageSymptomDto(lt("s"), mapOf("treatment:x" to 1))))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }

    @Test
    fun `validateStructure rejects a non-positive weight`() {
        val g = TriageGraphDto("a", mapOf("a" to TriageNodeDto(lt("q"), symptoms = listOf(TriageSymptomDto(lt("s"), mapOf("specialty:cardiology" to 0))))))
        assertThrows<IllegalArgumentException> { TriageService.validateStructure(g) }
    }
}
