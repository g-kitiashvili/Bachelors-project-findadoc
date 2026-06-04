package com.findadoc.api.service

import com.findadoc.api.exception.SpecialtyNotFoundException
import com.findadoc.api.repository.SpecialtyRepository
import com.findadoc.api.web.dto.SpecialtyDetailDto
import com.findadoc.api.web.dto.SpecialtyListItemDto
import org.springframework.stereotype.Service

@Service
class SpecialtyService(
    private val specialtyRepository: SpecialtyRepository,
) {
    fun listAll(
        region: String?,
        city: String?,
        clinicSlugs: List<String> = emptyList(),
        treatsChildren: Boolean = false,
        treatsAdults: Boolean = false,
    ): List<SpecialtyListItemDto> =
        specialtyRepository.findAllWithDoctorCount(region, city, clinicSlugs, treatsChildren, treatsAdults)

    fun getBySlug(slug: String): SpecialtyDetailDto {
        val specialty = specialtyRepository.findBySlug(slug)
            ?: throw SpecialtyNotFoundException(slug)
        return SpecialtyDetailDto(
            slug = specialty.slug,
            nameKa = specialty.nameKa,
            nameEn = specialty.nameEn,
            descriptionKa = specialty.descriptionKa,
            descriptionEn = specialty.descriptionEn,
            doctorCount = specialtyRepository.countDoctorsBySlug(slug),
            acceptingCount = specialtyRepository.countAcceptingBySlug(slug),
            treatsChildrenCount = specialtyRepository.countTreatsChildrenBySlug(slug),
        )
    }
}
