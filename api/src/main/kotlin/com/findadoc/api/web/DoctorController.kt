package com.findadoc.api.web

import com.findadoc.api.service.DoctorService
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.PageResponseDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/doctors")
@Tag(name = "Doctors", description = "Read access to scraped doctor records.")
class DoctorController(
    private val doctorService: DoctorService,
) {
    @Operation(summary = "List doctors")
    @GetMapping
    fun getAll(
        @RequestParam(defaultValue = "1") page: Int,
        @RequestParam(defaultValue = "5") pageSize: Int,
        @RequestParam(required = false) q: String?,
        @RequestParam(required = false) specialty: String?,
        @RequestParam(required = false) region: String?,
        @RequestParam(required = false) city: String?,
        @RequestParam(required = false) sort: String?,
    ): PageResponseDto<DoctorListItemDto> {
        val safePage = maxOf(page, 1)
        val safePageSize = pageSize.coerceIn(1, 50)
        val trimmedQ = q?.trim()?.take(100)?.takeIf { it.isNotEmpty() }
        val slugs = specialty?.split(',')
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }
            ?: emptyList()
        val regionSlug = region?.trim()?.takeIf { it.isNotEmpty() }
        val citySlug = city?.trim()?.takeIf { it.isNotEmpty() }
        val sortMode = sort?.trim()?.lowercase()?.takeIf { it == "relevancy" || it == "atoz" || it == "ztoa" }
        return doctorService.list(safePage, safePageSize, trimmedQ, slugs, regionSlug, citySlug, sortMode)
    }

    @Operation(summary = "Get a doctor by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): DoctorProfileDto =
        doctorService.getBySlug(slug)
}
