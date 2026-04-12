package com.findadoc.api.service

import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.dto.toListItemDto
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
    ): PageResponseDto<DoctorListItemDto> {
        val pageable = PageRequest.of(page - 1, pageSize)
        val result = doctorRepository.findFiltered(
            hasQ = q != null,
            q = q?.lowercase() ?: "",
            threshold = FUZZY_THRESHOLD,
            hasSpecialty = specialtySlugs.isNotEmpty(),
            specialtySlugs = specialtySlugs.ifEmpty { listOf("__none__") },
            hasRegion = region != null,
            region = region ?: "",
            hasCity = city != null,
            city = city ?: "",
            pageable = pageable,
        )
        return PageResponseDto(
            items = result.content.map { it.toListItemDto() },
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

    companion object {
        private const val FUZZY_THRESHOLD = 0.30
    }
}
