package com.findadoc.api.service

import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.dto.toProfileDto
import org.springframework.data.domain.PageRequest
import org.springframework.stereotype.Service

@Service
class DoctorService(
    private val doctorRepository: DoctorRepository,
) {
    fun list(
        page: Int,
        pageSize: Int,
        q: String?,
        specialtySlugs: List<String>,
        region: String?,
        city: String?,
        sort: String?,
    ): PageResponseDto<DoctorListItemDto> {
        val pageable = PageRequest.of(page - 1, pageSize)
        val filter = DoctorFilter(
            q = q?.lowercase(),
            specialtySlugs = specialtySlugs,
            region = region,
            city = city,
        )
        val result = doctorRepository.findFiltered(filter, sort, pageable)
        return PageResponseDto(
            items = result.content,
            page = page,
            pageSize = pageSize,
            total = result.totalElements,
        )
    }

    fun getBySlug(slug: String): DoctorProfileDto {
        val doctor = doctorRepository.findBySlug(slug)
            ?: throw DoctorNotFoundException(slug)
        return doctor.toProfileDto()
    }
}
