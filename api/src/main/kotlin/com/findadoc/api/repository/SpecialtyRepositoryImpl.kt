package com.findadoc.api.repository

import com.findadoc.api.search.RankedTarget
import com.findadoc.api.search.SearchTargetType
import com.findadoc.api.web.dto.SpecialtyListItemDto
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

    override fun searchRank(q: String, threshold: Double, limit: Int): List<RankedTarget> {
        val score = DSL.field(
            "greatest(" +
                "word_similarity({0}, lower(s.name_en)), " +
                "word_similarity({0}, lower(s.name_ka)), " +
                "coalesce((select 1.0 from specialty_alias a " +
                "where a.specialty_id = s.id and (lower(a.term) = {0} or regexp_replace(lower(a.term), 's$', '') = regexp_replace({0}, 's$', '')) limit 1), 0))",
            SQLDataType.DOUBLE, DSL.`val`(q),
        ).`as`("score")
        val isExact = DSL.field(
            "(lower(s.name_en) = {0} or lower(s.name_ka) = {0} or exists " +
                "(select 1 from specialty_alias a where a.specialty_id = s.id and (lower(a.term) = {0} or regexp_replace(lower(a.term), 's$', '') = regexp_replace({0}, 's$', ''))))",
            SQLDataType.BOOLEAN, DSL.`val`(q),
        ).`as`("is_exact")
        val doctorCount = DSL.field(
            "(select count(*) from doctor_specialty ds join doctor d on d.id = ds.doctor_id " +
                "where ds.specialty_id = s.id and d.status = 'ACTIVE')",
            SQLDataType.BIGINT,
        ).`as`("doctor_count")
        val matches = DSL.condition(
            "(word_similarity({0}, lower(s.name_en)) > {1} or word_similarity({0}, lower(s.name_ka)) > {1} " +
                "or exists (select 1 from specialty_alias a where a.specialty_id = s.id " +
                "and (lower(a.term) = {0} or regexp_replace(lower(a.term), 's$', '') = regexp_replace({0}, 's$', ''))))",
            DSL.`val`(q), DSL.`val`(threshold),
        )
        return dsl.select(DSL.field("s.slug"), DSL.field("s.name_en"), DSL.field("s.name_ka"), score, isExact, doctorCount)
            .from("specialty s")
            .where(matches)
            .orderBy(DSL.field("is_exact").desc(), DSL.field("score").desc(), DSL.field("doctor_count").desc())
            .limit(limit)
            .fetch { r ->
                RankedTarget(
                    type = SearchTargetType.SPECIALTY,
                    slug = r.get("s.slug", String::class.java),
                    nameEn = r.get("s.name_en", String::class.java),
                    nameKa = r.get("s.name_ka", String::class.java),
                    score = r.get("score", Double::class.java),
                    exact = r.get("is_exact", Boolean::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }
    }
}
