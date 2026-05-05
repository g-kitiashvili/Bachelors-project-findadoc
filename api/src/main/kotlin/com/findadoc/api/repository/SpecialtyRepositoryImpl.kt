package com.findadoc.api.repository

import com.findadoc.api.web.dto.SpecialtyListItemDto
import com.findadoc.api.web.dto.SpecialtySuggestionDto
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
import org.springframework.stereotype.Repository

@Repository
class SpecialtyRepositoryImpl(
    private val dsl: DSLContext,
) : SpecialtyRepositoryCustom {

    override fun countDoctorsBySlug(slug: String): Long = countBySlug(slug, null)

    override fun countAcceptingBySlug(slug: String): Long =
        countBySlug(slug, DSL.field("d.is_accepting_new_patients", Boolean::class.java).isTrue)

    override fun countTreatsChildrenBySlug(slug: String): Long =
        countBySlug(slug, DSL.field("d.treats_children", Boolean::class.java).isTrue)

    private fun countBySlug(slug: String, extra: Condition?): Long {
        var cond = DSL.field("s.slug").eq(slug).and(DSL.field("d.status").eq("ACTIVE"))
        if (extra != null) cond = cond.and(extra)
        return dsl.selectCount()
            .from("doctor_specialty ds")
            .join("specialty s").on("s.id = ds.specialty_id")
            .join("doctor d").on("d.id = ds.doctor_id")
            .where(cond)
            .fetchOne(0, Long::class.java) ?: 0L
    }

    override fun autocomplete(q: String, threshold: Double, limit: Int): List<SpecialtySuggestionDto> {
        val sim = DSL.greatest(
            DSL.field("word_similarity({0}, lower(s.name_en))", SQLDataType.DOUBLE, DSL.`val`(q)),
            DSL.field("word_similarity({0}, lower(s.name_ka))", SQLDataType.DOUBLE, DSL.`val`(q)),
        )
        return dsl.select(DSL.field("s.slug"), DSL.field("s.name_en"), DSL.field("s.name_ka"))
            .from("specialty s")
            .where(sim.gt(threshold))
            .orderBy(sim.desc(), DSL.field("s.sort_order").asc())
            .limit(limit)
            .fetch { r ->
                SpecialtySuggestionDto(
                    slug = r.get("s.slug", String::class.java),
                    nameEn = r.get("s.name_en", String::class.java),
                    nameKa = r.get("s.name_ka", String::class.java),
                )
            }
    }

    override fun findAllWithDoctorCount(
        region: String?,
        city: String?,
        clinicSlugs: List<String>,
    ): List<SpecialtyListItemDto> {
        val conditions = mutableListOf<Condition>(
            DSL.field("d.id").isNull.or(DSL.field("d.status").eq("ACTIVE"))
        )
        if (region != null) {
            conditions += DSL.field("reg.slug").eq(region).or(DSL.field("loc.slug").eq(region))
        }
        if (city != null) {
            conditions += DSL.field("loc.slug").eq(city)
        }
        if (clinicSlugs.isNotEmpty()) {
            conditions += DSL.exists(
                DSL.selectOne().from("doctor_clinic dc").join("clinic c").on("c.id = dc.clinic_id")
                    .where(DSL.field("dc.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("c.slug").`in`(clinicSlugs)),
            )
        }

        return dsl.select(
            DSL.field("s.slug"),
            DSL.field("s.name_ka"),
            DSL.field("s.name_en"),
            DSL.count(DSL.field("d.id")).`as`("doctor_count"),
        )
            .from("specialty s")
            .leftJoin("doctor_specialty ds").on("ds.specialty_id = s.id")
            .leftJoin("doctor d").on("d.id = ds.doctor_id")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .where(conditions)
            .groupBy(
                DSL.field("s.id"),
                DSL.field("s.slug"),
                DSL.field("s.name_ka"),
                DSL.field("s.name_en"),
                DSL.field("s.sort_order"),
            )
            .orderBy(DSL.field("s.sort_order").asc(), DSL.field("s.name_en").asc())
            .fetch { r ->
                SpecialtyListItemDto(
                    slug = r.get("s.slug", String::class.java),
                    nameKa = r.get("s.name_ka", String::class.java),
                    nameEn = r.get("s.name_en", String::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }
    }
}
