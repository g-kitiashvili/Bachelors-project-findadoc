package com.findadoc.api.web

import com.findadoc.api.service.ClinicService
import com.findadoc.api.web.dto.ClinicDetailDto
import com.findadoc.api.web.dto.ClinicListItemDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/clinics")
@Tag(name = "Clinics", description = "Clinic directory with per-clinic doctor counts.")
class ClinicController(
    private val clinicService: ClinicService,
) {
    @Operation(summary = "Top clinics with doctor counts, faceted by region/city/specialty and name search")
    @GetMapping
    fun getAll(
        @RequestParam(required = false) q: String?,
        @RequestParam(required = false) region: String?,
        @RequestParam(required = false) city: String?,
        @RequestParam(required = false) specialty: String?,
    ): Map<String, List<ClinicListItemDto>> {
        val slugs = specialty?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        return mapOf(
            "items" to clinicService.listFacet(
                q?.trim()?.takeIf { it.isNotEmpty() },
                region?.trim()?.takeIf { it.isNotEmpty() },
                city?.trim()?.takeIf { it.isNotEmpty() },
                slugs,
            ),
        )
    }

    @Operation(summary = "Get clinic by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): ClinicDetailDto = clinicService.getBySlug(slug)
}
