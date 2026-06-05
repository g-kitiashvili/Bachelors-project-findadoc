package com.findadoc.api.web

import com.findadoc.api.service.SpecialtyService
import com.findadoc.api.web.dto.SpecialtyDetailDto
import com.findadoc.api.web.dto.SpecialtyListItemDto
import com.findadoc.api.web.request.SpecialtyListParams
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/specialties")
@Tag(name = "Specialties", description = "Specialty taxonomy and per-specialty stats.")
class SpecialtyController(
    private val specialtyService: SpecialtyService,
) {
    @Operation(summary = "List all specialties with doctor counts, optionally scoped to a region or city")
    @GetMapping
    fun getAll(params: SpecialtyListParams): Map<String, List<SpecialtyListItemDto>> =
        mapOf("items" to specialtyService.listAll(
            params.regionSlug(), params.citySlug(), params.clinicSlugs(),
            params.treatsChildren, params.treatsAdults,
        ))

    @Operation(summary = "Get specialty by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): SpecialtyDetailDto =
        specialtyService.getBySlug(slug)
}
