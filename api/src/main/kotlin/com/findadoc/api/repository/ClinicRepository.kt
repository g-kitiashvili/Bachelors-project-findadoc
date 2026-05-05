package com.findadoc.api.repository

import com.findadoc.api.domain.Clinic
import org.springframework.data.jpa.repository.JpaRepository

interface ClinicRepository : JpaRepository<Clinic, Long>, ClinicRepositoryCustom {
    fun findBySlug(slug: String): Clinic?
}
