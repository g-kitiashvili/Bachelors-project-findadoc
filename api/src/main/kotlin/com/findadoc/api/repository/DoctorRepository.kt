package com.findadoc.api.repository

import com.findadoc.api.domain.Doctor
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface DoctorRepository : JpaRepository<Doctor, Long> {
    fun findBySlug(slug: String): Doctor?
    fun findByStatus(status: String, pageable: Pageable): Page<Doctor>

    @Query(
        value = """
            SELECT d FROM Doctor d
            WHERE d.status = 'ACTIVE'
              AND (:hasSpecialty = false OR EXISTS (
                    SELECT 1 FROM DoctorSpecialty ds
                    WHERE ds.doctor.id = d.id AND ds.specialty.slug IN :specialtySlugs
                  ))
              AND (:hasQ = false OR GREATEST(
                    function('word_similarity', :q, LOWER(d.fullNameEn)),
                    function('word_similarity', :q, LOWER(d.fullNameKa)),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyEn), '')),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyKa), ''))
                  ) > :threshold)
            ORDER BY
              CASE WHEN :hasQ = true THEN GREATEST(
                    function('word_similarity', :q, LOWER(d.fullNameEn)),
                    function('word_similarity', :q, LOWER(d.fullNameKa)),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyEn), '')),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyKa), ''))
                  ) END DESC,
              d.fullNameEn ASC,
              d.slug ASC
        """,
        countQuery = """
            SELECT COUNT(d) FROM Doctor d
            WHERE d.status = 'ACTIVE'
              AND (:hasSpecialty = false OR EXISTS (
                    SELECT 1 FROM DoctorSpecialty ds
                    WHERE ds.doctor.id = d.id AND ds.specialty.slug IN :specialtySlugs
                  ))
              AND (:hasQ = false OR GREATEST(
                    function('word_similarity', :q, LOWER(d.fullNameEn)),
                    function('word_similarity', :q, LOWER(d.fullNameKa)),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyEn), '')),
                    function('word_similarity', :q, COALESCE(LOWER(d.specialtyKa), ''))
                  ) > :threshold)
        """,
    )
    fun findFiltered(
        @Param("hasQ") hasQ: Boolean,
        @Param("q") q: String,
        @Param("threshold") threshold: Double,
        @Param("hasSpecialty") hasSpecialty: Boolean,
        @Param("specialtySlugs") specialtySlugs: List<String>,
        pageable: Pageable,
    ): Page<Doctor>
}
