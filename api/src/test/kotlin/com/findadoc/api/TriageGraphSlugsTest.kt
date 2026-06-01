package com.findadoc.api

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.test.assertTrue

class TriageGraphSlugsTest {
    private val yaml = ObjectMapper(YAMLFactory())

    private fun slugsOf(relPath: String): Set<String> {
        val f = File("../pipeline/pipeline/data/$relPath")
        assertTrue(f.exists(), "reference file not found: ${f.absolutePath}")
        return yaml.readTree(f).mapNotNull { it.get("slug")?.asText() }.toSet()
    }

    @Test
    fun `every triage result slug exists in the reference taxonomy`() {
        val specialtySlugs = slugsOf("specialties.yaml")
        val conditionSlugs = slugsOf("conditions.yaml")
        val graph = yaml.readTree(javaClass.getResourceAsStream("/triage/graph.yaml"))
        val missing = mutableListOf<String>()
        graph.get("nodes").fields().forEach { (nodeId, node) ->
            node.get("options")?.forEach { opt ->
                val result: JsonNode? = opt.get("result")
                if (result != null) {
                    val type = result.get("type").asText()
                    val slug = result.get("slug").asText()
                    val ok = when (type) {
                        "specialty" -> slug in specialtySlugs
                        "condition" -> slug in conditionSlugs
                        else -> false
                    }
                    if (!ok) missing += "$nodeId -> $type:$slug"
                }
            }
        }
        assertTrue(missing.isEmpty(), "triage results not found in taxonomy: $missing")
    }

    @Test
    fun `every symptom weight slug exists in the reference taxonomy`() {
        val specialtySlugs = slugsOf("specialties.yaml")
        val conditionSlugs = slugsOf("conditions.yaml")
        val graph = yaml.readTree(javaClass.getResourceAsStream("/triage/graph.yaml"))
        val missing = mutableListOf<String>()
        graph.get("nodes").fields().forEach { (nodeId, node) ->
            node.get("symptoms")?.forEach { sym ->
                val weights = sym.get("weights") ?: return@forEach
                weights.fieldNames().forEach { key ->
                    val type = key.substringBefore(':')
                    val slug = key.substringAfter(':')
                    val ok = when (type) {
                        "specialty" -> slug in specialtySlugs
                        "condition" -> slug in conditionSlugs
                        else -> false
                    }
                    if (!ok) missing += "$nodeId -> $key"
                }
            }
        }
        assertTrue(missing.isEmpty(), "triage weight slugs not found in taxonomy: $missing")
    }
}
