package com.findadoc.api.repository.jooq

import org.jooq.Condition
import org.jooq.Field
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType

data class DoctorFilter(
    val q: String? = null,
    val specialtySlugs: List<String> = emptyList(),
    val region: String? = null,
    val city: String? = null,
    val clinicSlugs: List<String> = emptyList(),
    val conditionSlugs: List<String> = emptyList(),
)

const val FUZZY_THRESHOLD = 0.30

private fun wordSim(q: String, column: String): Field<Double> =
    DSL.field("word_similarity({0}, lower({1}))", SQLDataType.DOUBLE, DSL.`val`(q), DSL.field(column))

fun relevance(q: String): Field<Double> = DSL.greatest(
    wordSim(q, "d.full_name_en"),
    wordSim(q, "d.full_name_ka"),
    DSL.field("word_similarity({0}, coalesce(lower(d.specialty_en), ''))", SQLDataType.DOUBLE, DSL.`val`(q)),
    DSL.field("word_similarity({0}, coalesce(lower(d.specialty_ka), ''))", SQLDataType.DOUBLE, DSL.`val`(q)),
)

fun doctorConditions(
    f: DoctorFilter,
    excludeSpecialty: Boolean = false,
    excludeClinic: Boolean = false,
): List<Condition> = buildList {
    add(DSL.field("d.status").eq("ACTIVE"))
    f.region?.let { add(DSL.field("reg.slug").eq(it).or(DSL.field("loc.slug").eq(it))) }
    f.city?.let { add(DSL.field("loc.slug").eq(it)) }
    if (!excludeSpecialty && f.specialtySlugs.isNotEmpty()) {
        add(
            DSL.exists(
                DSL.selectOne().from("doctor_specialty ds").join("specialty s").on("s.id = ds.specialty_id")
                    .where(DSL.field("ds.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("s.slug").`in`(f.specialtySlugs)),
            ),
        )
    }
    if (!excludeClinic && f.clinicSlugs.isNotEmpty()) {
        add(
            DSL.exists(
                DSL.selectOne().from("doctor_clinic dc").join("clinic c").on("c.id = dc.clinic_id")
                    .where(DSL.field("dc.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("c.slug").`in`(f.clinicSlugs)),
            ),
        )
    }
    if (f.conditionSlugs.isNotEmpty()) {
        add(
            DSL.exists(
                DSL.selectOne().from("doctor_specialty ds")
                    .join("condition_specialty cs").on("cs.specialty_id = ds.specialty_id")
                    .join("medical_condition mc").on("mc.id = cs.condition_id")
                    .where(DSL.field("ds.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("mc.slug").`in`(f.conditionSlugs)),
            ),
        )
    }
    f.q?.takeIf { it.isNotEmpty() }?.let { add(relevance(it).gt(FUZZY_THRESHOLD)) }
}
