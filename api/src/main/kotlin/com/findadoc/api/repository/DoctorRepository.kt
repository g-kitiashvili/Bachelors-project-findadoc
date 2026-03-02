package com.findadoc.api.repository

import com.findadoc.api.domain.Doctor
import org.springframework.data.jpa.repository.JpaRepository

interface DoctorRepository : JpaRepository<Doctor, Long> {
    fun findBySlug(slug: String): Doctor?
}
