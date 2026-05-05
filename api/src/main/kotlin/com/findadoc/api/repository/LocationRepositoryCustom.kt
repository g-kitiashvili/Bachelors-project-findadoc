package com.findadoc.api.repository

interface LocationRepositoryCustom {
    fun directDoctorCounts(specialtySlugs: List<String>, clinicSlugs: List<String>): List<Pair<Long, Long>>
}
