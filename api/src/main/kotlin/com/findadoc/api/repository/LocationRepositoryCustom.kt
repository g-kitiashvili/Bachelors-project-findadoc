package com.findadoc.api.repository

interface LocationRepositoryCustom {
    fun directDoctorCounts(specialtySlugs: List<String>, clinicSlugs: List<String>, treatsChildren: Boolean, treatsAdults: Boolean): List<Pair<Long, Long>>
}
