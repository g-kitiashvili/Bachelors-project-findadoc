package com.findadoc.api.repository

import com.findadoc.api.domain.MedicalCondition
import org.springframework.data.jpa.repository.JpaRepository

interface MedicalConditionRepository : JpaRepository<MedicalCondition, Long>, MedicalConditionRepositoryCustom {
    fun findBySlug(slug: String): MedicalCondition?
}
