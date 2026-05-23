package com.findadoc.api.repository

import com.findadoc.api.domain.Doctor
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

interface DoctorRepository : JpaRepository<Doctor, Long>, DoctorRepositoryCustom {
    fun findBySlug(slug: String): Doctor?
    fun findByStatus(status: String, pageable: Pageable): Page<Doctor>

    @Query(
        value = "SELECT c.slug FROM doctor m JOIN doctor c ON m.merged_into_id = c.id WHERE m.slug = :slug AND m.status = 'MERGED'",
        nativeQuery = true
    )
    fun findCanonicalSlugByMergedSlug(slug: String): String?
}
