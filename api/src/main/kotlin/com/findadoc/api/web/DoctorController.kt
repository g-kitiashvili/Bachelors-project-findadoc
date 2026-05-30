package com.findadoc.api.web

import com.findadoc.api.service.DoctorNotFoundException
import com.findadoc.api.service.DoctorService
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.MapPinDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.dto.toProfileDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
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
        @RequestParam(required = false) clinic: String?,
        @RequestParam(required = false) condition: String?,
        @RequestParam(name = "treats_children", required = false) treatsChildren: Boolean?,
        @RequestParam(name = "treats_adults", required = false) treatsAdults: Boolean?,
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
        val clinicSlugs = clinic?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        val conditionSlugs = condition?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        return doctorService.list(
            safePage, safePageSize, trimmedQ, slugs, regionSlug, citySlug, sortMode, clinicSlugs, conditionSlugs,
            treatsChildren == true, treatsAdults == true,
        )
    }

    @Operation(summary = "Clinic map pins, optionally within a radius of a center point")
    @GetMapping("/map-pins")
    fun mapPins(
        @RequestParam(required = false) center: String?,
        @RequestParam(name = "radius_km", required = false) radiusKm: Double?,
        @RequestParam(required = false) q: String?,
        @RequestParam(required = false) specialty: String?,
        @RequestParam(required = false) region: String?,
        @RequestParam(required = false) city: String?,
        @RequestParam(required = false) clinic: String?,
        @RequestParam(required = false) condition: String?,
    ): Map<String, List<MapPinDto>> {
        val parts = center?.split(',')?.map { it.trim() }
        val lat = parts?.getOrNull(0)?.toDoubleOrNull()
        val lng = parts?.getOrNull(1)?.toDoubleOrNull()
        val trimmedQ = q?.trim()?.take(100)?.takeIf { it.isNotEmpty() }
        val slugs = specialty?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        val regionSlug = region?.trim()?.takeIf { it.isNotEmpty() }
        val citySlug = city?.trim()?.takeIf { it.isNotEmpty() }
        val clinicSlugs = clinic?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        val conditionSlugs = condition?.split(',')?.map { it.trim() }?.filter { it.isNotEmpty() } ?: emptyList()
        return mapOf(
            "pins" to doctorService.mapPins(
                lat, lng, radiusKm, trimmedQ, slugs, regionSlug, citySlug, clinicSlugs, conditionSlugs,
            ),
        )
    }

    @Operation(summary = "Doctors similar to the given one (same specialty, ranked by shared specialties and proximity)")
    @GetMapping("/{slug}/similar")
    fun similar(
        @PathVariable slug: String,
        @RequestParam(defaultValue = "6") limit: Int,
    ): List<DoctorListItemDto> = doctorService.similar(slug, limit.coerceIn(1, 24))

    @Operation(summary = "Get a doctor by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): ResponseEntity<DoctorProfileDto> {
        val canonicalSlug = doctorService.canonicalSlugForMerged(slug)
        if (canonicalSlug != null) {
            return ResponseEntity.status(HttpStatus.MOVED_PERMANENTLY)
                .location(java.net.URI.create("/api/v1/doctors/$canonicalSlug"))
                .build()
        }
        val doctor = doctorService.findEntityBySlug(slug) ?: throw DoctorNotFoundException(slug)
        return ResponseEntity.ok(doctor.toProfileDto())
    }
}
