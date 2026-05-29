package com.findadoc.api.repository

import com.findadoc.api.web.dto.ClinicBranchDto
import com.findadoc.api.web.dto.ClinicBrandRefDto
import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.ClinicSuggestionDto

interface ClinicRepositoryCustom {
    fun facet(q: String?, region: String?, city: String?, specialtySlugs: List<String>, located: Boolean, collapseBrands: Boolean, limit: Int, offset: Int): List<ClinicListItemDto>
    fun countFacet(q: String?, region: String?, city: String?, specialtySlugs: List<String>, located: Boolean, collapseBrands: Boolean): Long
    fun countDoctorsBySlug(slug: String): Long
    fun autocomplete(q: String, threshold: Double, limit: Int): List<ClinicSuggestionDto>
    fun coordinatesBySlug(slug: String): Pair<Double, Double>?
    fun brandBySlug(slug: String): ClinicBrandRefDto?
    fun branchesBySlug(slug: String): List<ClinicBranchDto>
}
