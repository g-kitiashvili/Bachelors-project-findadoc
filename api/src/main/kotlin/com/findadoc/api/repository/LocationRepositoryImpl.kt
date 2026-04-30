package com.findadoc.api.repository

import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.springframework.stereotype.Repository

@Repository
class LocationRepositoryImpl(
    private val dsl: DSLContext,
) : LocationRepositoryCustom {

    override fun directDoctorCounts(specialtySlugs: List<String>): List<Pair<Long, Long>> {
        val conditions = mutableListOf<Condition>(
            DSL.field("d.status").eq("ACTIVE"),
            DSL.field("d.location_id").isNotNull,
        )
        if (specialtySlugs.isNotEmpty()) {
            conditions += DSL.exists(
                DSL.selectOne().from("doctor_specialty ds").join("specialty s").on("s.id = ds.specialty_id")
                    .where(DSL.field("ds.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("s.slug").`in`(specialtySlugs)),
            )
        }
        return dsl.select(DSL.field("d.location_id"), DSL.count().`as`("cnt"))
            .from("doctor d")
            .where(conditions)
            .groupBy(DSL.field("d.location_id"))
            .fetch { r -> r.get("d.location_id", Long::class.java) to r.get("cnt", Long::class.java) }
    }
}
