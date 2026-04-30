package com.findadoc.api.repository

import com.findadoc.api.domain.Specialty
import org.springframework.data.jpa.repository.JpaRepository

interface SpecialtyRepository : JpaRepository<Specialty, Long>, SpecialtyRepositoryCustom {
    fun findBySlug(slug: String): Specialty?
}
