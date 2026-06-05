package com.findadoc.api.web

import com.findadoc.api.service.ClinicService
import com.findadoc.api.web.dto.ClinicDetailDto
import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.request.ClinicListParams
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/clinics")
@Tag(name = "Clinics", description = "Clinic directory with per-clinic doctor counts.")
class ClinicController(
    private val clinicService: ClinicService,
) {
    @Operation(summary = "Clinics with doctor counts, faceted by region/city/specialty and name search, paginated")
    @GetMapping
    fun getAll(params: ClinicListParams): PageResponseDto<ClinicListItemDto> =
        clinicService.listFacet(
            params.query(),
            params.regionSlug(),
            params.citySlug(),
            params.specialtySlugs(),
            params.safePage(),
            params.safePageSize(),
            params.located,
            params.collapse,
            params.treatsChildren,
            params.treatsAdults,
        )

    @Operation(summary = "Get clinic by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): ClinicDetailDto = clinicService.getBySlug(slug)
}
