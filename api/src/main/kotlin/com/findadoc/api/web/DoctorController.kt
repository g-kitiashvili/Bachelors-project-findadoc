package com.findadoc.api.web

import com.findadoc.api.exception.DoctorNotFoundException
import com.findadoc.api.service.DoctorService
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.MapPinDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.dto.toProfileDto
import com.findadoc.api.web.request.DoctorListParams
import com.findadoc.api.web.request.MapPinsParams
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
    fun getAll(params: DoctorListParams): PageResponseDto<DoctorListItemDto> =
        doctorService.list(
            params.safePage(), params.safePageSize(), params.query(), params.specialtySlugs(),
            params.regionSlug(), params.citySlug(), params.sortMode(), params.clinicSlugs(),
            params.conditionSlugs(), params.treatsChildren, params.treatsAdults,
        )

    @Operation(summary = "Clinic map pins, optionally within a radius of a center point")
    @GetMapping("/map-pins")
    fun mapPins(params: MapPinsParams): Map<String, List<MapPinDto>> =
        mapOf(
            "pins" to doctorService.mapPins(
                params.lat(), params.lng(), params.radiusKm, params.query(), params.specialtySlugs(),
                params.regionSlug(), params.citySlug(), params.clinicSlugs(), params.conditionSlugs(),
                params.treatsChildren, params.treatsAdults,
            ),
        )

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
