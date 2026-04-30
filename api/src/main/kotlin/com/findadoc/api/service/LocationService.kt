package com.findadoc.api.service

import com.findadoc.api.repository.LocationRepository
import com.findadoc.api.web.dto.LocationCityDto
import com.findadoc.api.web.dto.LocationRegionDto
import org.springframework.stereotype.Service

@Service
class LocationService(
    private val locationRepository: LocationRepository,
) {
    fun listAll(specialtySlugs: List<String> = emptyList()): List<LocationRegionDto> {
        val counts = locationRepository.directDoctorCounts(specialtySlugs).toMap()
        val all = locationRepository.findAllByOrderBySortOrderAscNameEnAsc()
        val citiesByRegion = all.filter { it.parent != null }.groupBy { it.parent!!.id }

        return all.filter { it.parent == null }.map { region ->
            val cities = (citiesByRegion[region.id] ?: emptyList()).map { city ->
                LocationCityDto(
                    slug = city.slug,
                    nameKa = city.nameKa,
                    nameEn = city.nameEn,
                    doctorCount = counts[city.id] ?: 0L,
                )
            }
            LocationRegionDto(
                slug = region.slug,
                nameKa = region.nameKa,
                nameEn = region.nameEn,
                doctorCount = (counts[region.id] ?: 0L) + cities.sumOf { it.doctorCount },
                cities = cities,
            )
        }
    }
}
