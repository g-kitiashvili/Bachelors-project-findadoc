package com.findadoc.api.web

import com.findadoc.api.service.TriageService
import com.findadoc.api.web.dto.TriageGraphDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/triage")
@Tag(name = "Triage", description = "Curated guided-question graph that routes to a specialty or condition.")
class TriageController(private val triageService: TriageService) {
    @Operation(summary = "Get the triage question-graph")
    @GetMapping
    fun graph(): TriageGraphDto = triageService.getGraph()
}
