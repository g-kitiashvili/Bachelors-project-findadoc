package com.findadoc.api.service

import com.findadoc.api.repository.ClinicRepository
import com.findadoc.api.web.dto.ClinicDetailDto
import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.PageResponseDto
import org.springframework.stereotype.Service

@Service
class ClinicService(
    private val clinicRepository: ClinicRepository,
) {
    fun listFacet(
        q: String?,
        region: String?,
        city: String?,
        specialtySlugs: List<String>,
        page: Int,
        pageSize: Int,
    ): PageResponseDto<ClinicListItemDto> {
        val items = clinicRepository.facet(q, region, city, specialtySlugs, pageSize, (page - 1) * pageSize)
        val total = clinicRepository.countFacet(q, region, city, specialtySlugs)
        return PageResponseDto(items = items, page = page, pageSize = pageSize, total = total)
    }

    fun getBySlug(slug: String): ClinicDetailDto {
        val c = clinicRepository.findBySlug(slug) ?: throw ClinicNotFoundException(slug)
        return ClinicDetailDto(c.slug, c.nameKa, c.nameEn, c.address, c.addressEn, c.phone, c.website, clinicRepository.countDoctorsBySlug(slug))
    }
}
