package com.findadoc.api.service

import com.findadoc.api.domain.Specialty
import com.findadoc.api.repository.SpecialtyRepository
import com.findadoc.api.web.dto.SpecialtyDetailDto
import com.findadoc.api.web.dto.SpecialtyListItemDto
import org.springframework.stereotype.Service

@Service
class SpecialtyService(
    private val specialtyRepository: SpecialtyRepository,
) {
    fun listAll(): List<SpecialtyListItemDto> =
        specialtyRepository.findAllWithDoctorCount().map { row ->
            val specialty = row[0] as Specialty
            SpecialtyListItemDto(
                slug = specialty.slug,
                nameKa = specialty.nameKa,
                nameEn = specialty.nameEn,
                doctorCount = (row[1] as Number).toLong(),
            )
        }

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
