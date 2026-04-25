package com.findadoc.api.web

import com.findadoc.api.service.LocationService
import com.findadoc.api.web.dto.LocationRegionDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/locations")
@Tag(name = "Locations", description = "Region/city taxonomy with per-node doctor counts.")
class LocationController(
    private val locationService: LocationService,
) {
    @Operation(summary = "List regions with nested cities and active-doctor counts, optionally scoped to specialties")
    @GetMapping
    fun getAll(
        @RequestParam(required = false) specialty: String?,
    ): Map<String, List<LocationRegionDto>> {
        val slugs = specialty?.split(',')
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }
            ?: emptyList()
        return mapOf("items" to locationService.listAll(slugs))
    }
}
