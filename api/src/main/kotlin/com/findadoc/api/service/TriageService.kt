package com.findadoc.api.service

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.findadoc.api.web.dto.TriageGraphDto
import com.findadoc.api.web.dto.TriageNodeDto
import com.findadoc.api.web.dto.TriageSymptomDto
import jakarta.annotation.PostConstruct
import org.springframework.stereotype.Service

@Service
class TriageService {
    private lateinit var graph: TriageGraphDto

    @PostConstruct
    fun load() {
        val yaml = ObjectMapper(YAMLFactory()).findAndRegisterModules()
        val stream = javaClass.getResourceAsStream("/triage/graph.yaml")
            ?: error("triage/graph.yaml not found on classpath")
        val parsed = stream.use { yaml.readValue(it, TriageGraphDto::class.java) }
        validateStructure(parsed)
        graph = parsed
    }

    fun getGraph(): TriageGraphDto = graph

    companion object {
        private val VALID_RESULT_TYPES = setOf("specialty", "condition")

        fun validateStructure(g: TriageGraphDto) {
            require(g.nodes.containsKey(g.start)) { "start node '${g.start}' is not in nodes" }
            g.nodes.forEach { (id, node) ->
                val hasOptions = node.options.isNotEmpty()
                val hasSymptoms = !node.symptoms.isNullOrEmpty()
                require(hasOptions != hasSymptoms) {
                    "node '$id' must have exactly one of options/symptoms"
                }
                if (hasOptions) validateOptions(id, node, g)
                if (hasSymptoms) validateSymptoms(id, node.symptoms!!)
            }
            detectCycles(g)
        }

        private fun validateOptions(id: String, node: TriageNodeDto, g: TriageGraphDto) {
            node.options.forEach { opt ->
                require((opt.next != null) != (opt.result != null)) {
                    "an option in '$id' must have exactly one of next/result"
                }
                opt.next?.let { require(g.nodes.containsKey(it)) { "option in '$id' points to missing node '$it'" } }
                opt.result?.let { require(it.type in VALID_RESULT_TYPES) { "result type '${it.type}' must be specialty|condition" } }
            }
        }

        private fun validateSymptoms(id: String, symptoms: List<TriageSymptomDto>) {
            symptoms.forEach { sym ->
                require(sym.weights.isNotEmpty()) { "a symptom in '$id' has no weights" }
                sym.weights.forEach { (key, weight) ->
                    val type = key.substringBefore(':', "")
                    require(type in VALID_RESULT_TYPES && key.contains(':')) {
                        "weight key '$key' in '$id' must be 'specialty:<slug>' or 'condition:<slug>'"
                    }
                    require(weight > 0) { "weight for '$key' in '$id' must be positive" }
                }
            }
        }

        private fun detectCycles(g: TriageGraphDto) {
            val visiting = mutableSetOf<String>()
            val done = mutableSetOf<String>()
            fun dfs(id: String) {
                if (id in done) return
                require(id !in visiting) { "cycle detected at node '$id'" }
                visiting += id
                g.nodes[id]?.options?.forEach { opt -> opt.next?.let { dfs(it) } }
                visiting -= id
                done += id
            }
            dfs(g.start)
        }
    }
}
