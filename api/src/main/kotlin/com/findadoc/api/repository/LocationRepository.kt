package com.findadoc.api.repository

import com.findadoc.api.domain.Location
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface LocationRepository : JpaRepository<Location, Long> {
    fun findAllByOrderBySortOrderAscNameEnAsc(): List<Location>

    @Query(
        """
        SELECT d.location.id, COUNT(d) FROM Doctor d
        WHERE d.status = 'ACTIVE' AND d.location.id IS NOT NULL
          AND (:hasSpecialty = false OR EXISTS (
                SELECT 1 FROM DoctorSpecialty ds
                WHERE ds.doctor.id = d.id AND ds.specialty.slug IN :specialtySlugs
              ))
        GROUP BY d.location.id
        """
    )
    fun directDoctorCounts(
        @Param("hasSpecialty") hasSpecialty: Boolean,
        @Param("specialtySlugs") specialtySlugs: List<String>,
    ): List<Array<Any>>
}
