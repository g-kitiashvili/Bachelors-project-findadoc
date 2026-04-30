package com.findadoc.api.repository

import com.findadoc.api.domain.Doctor
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository

interface DoctorRepository : JpaRepository<Doctor, Long>, DoctorRepositoryCustom {
    fun findBySlug(slug: String): Doctor?
    fun findByStatus(status: String, pageable: Pageable): Page<Doctor>
}
