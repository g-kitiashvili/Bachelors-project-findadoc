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
    val treatsChildren: Boolean = false,
    val treatsAdults: Boolean = false,
    val nameOnly: Boolean = false,
)

const val FUZZY_THRESHOLD = 0.30

// Georgian surnames overwhelmingly end in -შვილი or -ძე (Latin -shvili / -dze). Those
// suffixes' trigrams match thousands of unrelated surnames, so a full-surname query clears
// the fuzzy threshold against everyone. Match on the distinctive stem by dropping the suffix
// from the query; a bare suffix collapses to an empty stem and matches no one.
private val PATRONYMIC_SUFFIX = Regex("(შვილი|ძე|shvili|dze)$", RegexOption.IGNORE_CASE)

private fun nameStem(q: String): String = PATRONYMIC_SUFFIX.replace(q.trim(), "")

private fun wordSim(q: String, column: String): Field<Double> =
    DSL.field("word_similarity({0}, lower({1}))", SQLDataType.DOUBLE, DSL.`val`(q), DSL.field(column))

fun relevance(q: String): Field<Double> {
    val stem = nameStem(q)
    return DSL.greatest(
        wordSim(stem, "d.full_name_en"),
        wordSim(stem, "d.full_name_ka"),
        DSL.field("word_similarity({0}, coalesce(lower(d.specialty_en), ''))", SQLDataType.DOUBLE, DSL.`val`(q)),
        DSL.field("word_similarity({0}, coalesce(lower(d.specialty_ka), ''))", SQLDataType.DOUBLE, DSL.`val`(q)),
    )
}

fun nameRelevance(q: String): Field<Double> {
    val stem = nameStem(q)
    return DSL.greatest(
        wordSim(stem, "d.full_name_en"),
        wordSim(stem, "d.full_name_ka"),
    )
}

fun doctorConditions(
    f: DoctorFilter,
    excludeSpecialty: Boolean = false,
    excludeClinic: Boolean = false,
): List<Condition> = buildList {
    add(DSL.field("d.status").eq("ACTIVE"))
    f.region?.let { add(DSL.field("reg.slug").eq(it).or(DSL.field("loc.slug").eq(it))) }
    f.city?.let { add(DSL.field("loc.slug").eq(it)) }
    if (!excludeSpecialty && f.specialtySlugs.isNotEmpty()) {
        // Parent-aware: selecting a parent specialty includes doctors mapped to any of
        // its sub-specialties; selecting a child narrows to just that one.
        add(
            DSL.exists(
                DSL.selectOne().from("doctor_specialty ds").join("specialty s").on("s.id = ds.specialty_id")
                    .where(DSL.field("ds.doctor_id").eq(DSL.field("d.id")))
                    .and(
                        DSL.field("s.slug").`in`(f.specialtySlugs).or(
                            DSL.field("s.parent_id").`in`(
                                DSL.select(DSL.field("id")).from("specialty")
                                    .where(DSL.field("slug").`in`(f.specialtySlugs)),
                            ),
                        ),
                    ),
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
    if (f.treatsChildren) add(DSL.field("d.treats_children").eq(true))
    if (f.treatsAdults) add(DSL.field("d.treats_adults").eq(true))
    f.q?.takeIf { it.isNotEmpty() }?.let {
        add((if (f.nameOnly) nameRelevance(it) else relevance(it)).gt(FUZZY_THRESHOLD))
    }
}
