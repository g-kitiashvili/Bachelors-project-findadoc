package com.findadoc.api.repository

import com.findadoc.api.web.dto.SpecialtyListItemDto
import com.findadoc.api.web.dto.SpecialtySuggestionDto

interface SpecialtyRepositoryCustom {
    fun findAllWithDoctorCount(region: String?, city: String?): List<SpecialtyListItemDto>
    fun countDoctorsBySlug(slug: String): Long
    fun countAcceptingBySlug(slug: String): Long
    fun countTreatsChildrenBySlug(slug: String): Long
    fun autocomplete(q: String, threshold: Double, limit: Int): List<SpecialtySuggestionDto>
}
