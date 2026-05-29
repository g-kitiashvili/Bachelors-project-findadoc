package com.findadoc.api.repository

import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.MapPinDto
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable

interface DoctorRepositoryCustom {
    fun findFiltered(filter: DoctorFilter, sort: String?, pageable: Pageable): Page<DoctorListItemDto>
    fun mapPins(filter: DoctorFilter, centerLat: Double?, centerLng: Double?, radiusKm: Double?): List<MapPinDto>
}
