package com.findadoc.api.web

import com.findadoc.api.service.SpecialtyService
import com.findadoc.api.web.dto.SpecialtyDetailDto
import com.findadoc.api.web.dto.SpecialtyListItemDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/specialties")
@Tag(name = "Specialties", description = "Specialty taxonomy and per-specialty stats.")
class SpecialtyController(
    private val specialtyService: SpecialtyService,
) {
    @Operation(summary = "List all specialties with doctor counts, optionally scoped to a region or city")
    @GetMapping
    fun getAll(
        @RequestParam(required = false) region: String?,
        @RequestParam(required = false) city: String?,
    ): Map<String, List<SpecialtyListItemDto>> {
        val regionSlug = region?.trim()?.takeIf { it.isNotEmpty() }
        val citySlug = city?.trim()?.takeIf { it.isNotEmpty() }
        return mapOf("items" to specialtyService.listAll(regionSlug, citySlug))
    }

    @Operation(summary = "Get specialty by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): SpecialtyDetailDto =
        specialtyService.getBySlug(slug)
}
