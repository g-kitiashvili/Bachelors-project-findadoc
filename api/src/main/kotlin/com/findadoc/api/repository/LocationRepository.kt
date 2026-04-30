package com.findadoc.api.repository

import com.findadoc.api.domain.Location
import org.springframework.data.jpa.repository.JpaRepository

interface LocationRepository : JpaRepository<Location, Long>, LocationRepositoryCustom {
    fun findAllByOrderBySortOrderAscNameEnAsc(): List<Location>
}
