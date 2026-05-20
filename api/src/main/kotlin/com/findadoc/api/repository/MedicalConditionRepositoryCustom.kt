package com.findadoc.api.repository

import com.findadoc.api.search.RankedTarget
import com.findadoc.api.web.dto.MedicalConditionListItemDto

interface MedicalConditionRepositoryCustom {
    fun findAllWithDoctorCount(): List<MedicalConditionListItemDto>
    fun countDoctorsBySlug(slug: String): Long
    fun countAcceptingBySlug(slug: String): Long
    fun countTreatsChildrenBySlug(slug: String): Long
    fun searchRank(q: String, threshold: Double, limit: Int): List<RankedTarget>
}
