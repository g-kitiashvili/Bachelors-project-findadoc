package com.findadoc.api.service

import com.findadoc.api.repository.MedicalConditionRepository
import com.findadoc.api.web.dto.MedicalConditionDetailDto
import com.findadoc.api.web.dto.MedicalConditionListItemDto
import org.springframework.stereotype.Service

@Service
class MedicalConditionService(
    private val repository: MedicalConditionRepository,
) {
    fun listAll(): List<MedicalConditionListItemDto> = repository.findAllWithDoctorCount()

    fun getBySlug(slug: String): MedicalConditionDetailDto {
        val c = repository.findBySlug(slug) ?: throw MedicalConditionNotFoundException(slug)
        return MedicalConditionDetailDto(
            slug = c.slug, nameKa = c.nameKa, nameEn = c.nameEn,
            descriptionKa = c.descriptionKa, descriptionEn = c.descriptionEn,
            doctorCount = repository.countDoctorsBySlug(slug),
            acceptingCount = repository.countAcceptingBySlug(slug),
            treatsChildrenCount = repository.countTreatsChildrenBySlug(slug),
        )
    }
}
