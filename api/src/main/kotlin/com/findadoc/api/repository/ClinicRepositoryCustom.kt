package com.findadoc.api.repository

import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.ClinicSuggestionDto

interface ClinicRepositoryCustom {
    fun facet(q: String?, region: String?, city: String?, specialtySlugs: List<String>, limit: Int, offset: Int): List<ClinicListItemDto>
    fun countFacet(q: String?, region: String?, city: String?, specialtySlugs: List<String>): Long
    fun countDoctorsBySlug(slug: String): Long
    fun autocomplete(q: String, threshold: Double, limit: Int): List<ClinicSuggestionDto>
}
