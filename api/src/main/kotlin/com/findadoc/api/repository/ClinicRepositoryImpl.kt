package com.findadoc.api.repository

import com.findadoc.api.repository.jooq.FUZZY_THRESHOLD
import com.findadoc.api.web.dto.ClinicListItemDto
import com.findadoc.api.web.dto.ClinicSuggestionDto
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
import org.springframework.stereotype.Repository

@Repository
class ClinicRepositoryImpl(
    private val dsl: DSLContext,
) : ClinicRepositoryCustom {

    override fun facet(
        q: String?,
        region: String?,
        city: String?,
        specialtySlugs: List<String>,
        limit: Int,
    ): List<ClinicListItemDto> {
        val conditions = mutableListOf<Condition>(DSL.field("d.status").eq("ACTIVE"))
        region?.let { conditions += DSL.field("reg.slug").eq(it).or(DSL.field("loc.slug").eq(it)) }
        city?.let { conditions += DSL.field("loc.slug").eq(it) }
        if (specialtySlugs.isNotEmpty()) {
            conditions += DSL.exists(
                DSL.selectOne().from("doctor_specialty ds").join("specialty s").on("s.id = ds.specialty_id")
                    .where(DSL.field("ds.doctor_id").eq(DSL.field("d.id")))
                    .and(DSL.field("s.slug").`in`(specialtySlugs)),
            )
        }
        q?.takeIf { it.isNotEmpty() }?.let {
            conditions += DSL.greatest(
                DSL.field("word_similarity({0}, lower(c.name_en))", SQLDataType.DOUBLE, DSL.`val`(it)),
                DSL.field("word_similarity({0}, c.name_ka)", SQLDataType.DOUBLE, DSL.`val`(it)),
            ).gt(FUZZY_THRESHOLD)
        }
        return dsl.select(
            DSL.field("c.slug"),
            DSL.field("c.name_ka"),
            DSL.field("c.name_en"),
            DSL.count(DSL.field("d.id")).`as`("doctor_count"),
        )
            .from("clinic c")
            .join("doctor_clinic dc").on("dc.clinic_id = c.id")
            .join("doctor d").on("d.id = dc.doctor_id")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .where(conditions)
            .groupBy(DSL.field("c.id"), DSL.field("c.slug"), DSL.field("c.name_ka"), DSL.field("c.name_en"))
            .orderBy(DSL.count(DSL.field("d.id")).desc(), DSL.field("c.name_en").asc())
            .limit(limit)
            .fetch { r ->
                ClinicListItemDto(
                    slug = r.get("c.slug", String::class.java),
                    nameKa = r.get("c.name_ka", String::class.java),
                    nameEn = r.get("c.name_en", String::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }
    }

    override fun countDoctorsBySlug(slug: String): Long =
        dsl.selectCount().from("doctor_clinic dc").join("clinic c").on("c.id = dc.clinic_id").join("doctor d").on("d.id = dc.doctor_id")
            .where(DSL.field("c.slug").eq(slug).and(DSL.field("d.status").eq("ACTIVE")))
            .fetchOne(0, Long::class.java) ?: 0L

    override fun autocomplete(q: String, threshold: Double, limit: Int): List<ClinicSuggestionDto> {
        val sim = DSL.greatest(
            DSL.field("word_similarity({0}, lower(c.name_en))", SQLDataType.DOUBLE, DSL.`val`(q)),
            DSL.field("word_similarity({0}, c.name_ka)", SQLDataType.DOUBLE, DSL.`val`(q)),
        )
        return dsl.select(DSL.field("c.slug"), DSL.field("c.name_en"), DSL.field("c.name_ka"))
            .from("clinic c")
            .where(sim.gt(threshold))
            .orderBy(sim.desc(), DSL.field("c.name_en").asc())
            .limit(limit)
            .fetch { r ->
                ClinicSuggestionDto(
                    slug = r.get("c.slug", String::class.java),
                    nameEn = r.get("c.name_en", String::class.java),
                    nameKa = r.get("c.name_ka", String::class.java),
                )
            }
    }
}
