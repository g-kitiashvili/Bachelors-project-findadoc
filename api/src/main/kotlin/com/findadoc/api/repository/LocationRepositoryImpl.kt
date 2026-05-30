package com.findadoc.api.repository

import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.springframework.stereotype.Repository

@Repository
class LocationRepositoryImpl(
    private val dsl: DSLContext,
) : LocationRepositoryCustom {

    override fun directDoctorCounts(
        specialtySlugs: List<String>,
        clinicSlugs: List<String>,
        treatsChildren: Boolean,
        treatsAdults: Boolean,
    ): List<Pair<Long, Long>> {
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
        if (clinicSlugs.isNotEmpty()) {
            conditions += DSL.exists(
                DSL.selectOne().from("doctor_clinic dc").join("clinic c").on("c.id = dc.clinic_id")
                    .where(DSL.field("dc.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("c.slug").`in`(clinicSlugs)),
            )
        }
        if (treatsChildren) conditions += DSL.field("d.treats_children").eq(true)
        if (treatsAdults) conditions += DSL.field("d.treats_adults").eq(true)
        return dsl.select(DSL.field("d.location_id"), DSL.count().`as`("cnt"))
            .from("doctor d")
            .where(conditions)
            .groupBy(DSL.field("d.location_id"))
            .fetch { r -> r.get("d.location_id", Long::class.java) to r.get("cnt", Long::class.java) }
    }
}
