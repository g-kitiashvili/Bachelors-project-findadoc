package com.findadoc.api.service

import com.findadoc.api.repository.ClinicRepository
import com.findadoc.api.web.dto.ClinicDetailDto
import com.findadoc.api.web.dto.ClinicListItemDto
import org.springframework.stereotype.Service

@Service
class ClinicService(
    private val clinicRepository: ClinicRepository,
) {
    fun listFacet(q: String?, region: String?, city: String?, specialtySlugs: List<String>): List<ClinicListItemDto> =
        clinicRepository.facet(q, region, city, specialtySlugs, FACET_CAP)

    fun getBySlug(slug: String): ClinicDetailDto {
        val c = clinicRepository.findBySlug(slug) ?: throw ClinicNotFoundException(slug)
        return ClinicDetailDto(c.slug, c.nameKa, c.nameEn, c.address, c.phone, c.website, clinicRepository.countDoctorsBySlug(slug))
    }

    companion object {
        private const val FACET_CAP = 50
    }
}
