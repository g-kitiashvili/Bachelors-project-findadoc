package com.findadoc.api.web

import com.findadoc.api.service.MedicalConditionService
import com.findadoc.api.web.dto.MedicalConditionDetailDto
import com.findadoc.api.web.dto.MedicalConditionListItemDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/conditions")
@Tag(name = "Conditions", description = "Medical conditions mapped to specialties.")
class MedicalConditionController(
    private val service: MedicalConditionService,
) {
    @Operation(summary = "List all conditions with doctor counts")
    @GetMapping
    fun getAll(): Map<String, List<MedicalConditionListItemDto>> =
        mapOf("items" to service.listAll())

    @Operation(summary = "Get condition by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): MedicalConditionDetailDto =
        service.getBySlug(slug)
}
