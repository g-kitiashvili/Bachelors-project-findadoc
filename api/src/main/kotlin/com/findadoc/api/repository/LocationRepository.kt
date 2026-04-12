package com.findadoc.api.repository

import com.findadoc.api.domain.Location
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query

interface LocationRepository : JpaRepository<Location, Long> {
    fun findAllByOrderBySortOrderAscNameEnAsc(): List<Location>

    @Query(
        """
        SELECT d.location.id, COUNT(d) FROM Doctor d
        WHERE d.status = 'ACTIVE' AND d.location.id IS NOT NULL
        GROUP BY d.location.id
        """
    )
    fun directDoctorCounts(): List<Array<Any>>
}
