package com.findadoc.api.web

import com.findadoc.api.service.ClinicService
import com.findadoc.api.web.dto.ClinicDetailDto
import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.PageResponseDto
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
    @Operation(summary = "Clinics with doctor counts, faceted by region/city/specialty and name search, paginated")
    @GetMapping
    fun getAll(
        @RequestParam(required = false) q: String?,
        @RequestParam(required = false) region: String?,
        @RequestParam(required = false) city: String?,
        @RequestParam(required = false) specialty: String?,
        @RequestParam(required = false) located: Boolean?,
        @RequestParam(required = false) collapse: Boolean?,
        @RequestParam(name = "treats_children", required = false) treatsChildren: Boolean?,
        @RequestParam(name = "treats_adults", required = false) treatsAdults: Boolean?,
        @RequestParam(defaultValue = "1") page: Int,
        @RequestParam(defaultValue = "50") pageSize: Int,
    ): PageResponseDto<ClinicListItemDto> {
        val slugs = specialty?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        val safePage = maxOf(page, 1)
        val safeSize = pageSize.coerceIn(1, 100)
        return clinicService.listFacet(
            q?.trim()?.takeIf { it.isNotEmpty() },
            region?.trim()?.takeIf { it.isNotEmpty() },
            city?.trim()?.takeIf { it.isNotEmpty() },
            slugs,
            safePage,
            safeSize,
            located == true,
            collapse == true,
            treatsChildren == true,
            treatsAdults == true,
        )
    }

    @Operation(summary = "Get clinic by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): ClinicDetailDto = clinicService.getBySlug(slug)
}
