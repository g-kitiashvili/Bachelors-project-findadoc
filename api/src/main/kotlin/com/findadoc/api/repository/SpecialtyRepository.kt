package com.findadoc.api.repository

import com.findadoc.api.domain.Specialty
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

interface SpecialtyRepository : JpaRepository<Specialty, Long> {
    fun findBySlug(slug: String): Specialty?

    @Query(
        """
        SELECT s, COUNT(ds.doctor.id) FROM Specialty s
        LEFT JOIN DoctorSpecialty ds ON ds.specialty.id = s.id
            AND ds.doctor.status = 'ACTIVE'
        GROUP BY s
        ORDER BY s.sortOrder ASC, s.nameEn ASC
        """
    )
    fun findAllWithDoctorCount(): List<Array<Any>>

    @Query(
        """
        SELECT COUNT(ds) FROM DoctorSpecialty ds
        WHERE ds.specialty.slug = :slug AND ds.doctor.status = 'ACTIVE'
        """
    )
    fun countDoctorsBySlug(slug: String): Long

    @Query(
        """
        SELECT COUNT(ds) FROM DoctorSpecialty ds
        WHERE ds.specialty.slug = :slug
            AND ds.doctor.status = 'ACTIVE' AND ds.doctor.isAcceptingNewPatients = true
        """
    )
    fun countAcceptingBySlug(slug: String): Long

    @Query(
        """
        SELECT COUNT(ds) FROM DoctorSpecialty ds
        WHERE ds.specialty.slug = :slug
            AND ds.doctor.status = 'ACTIVE' AND ds.doctor.treatsChildren = true
        """
    )
    fun countTreatsChildrenBySlug(slug: String): Long
}
