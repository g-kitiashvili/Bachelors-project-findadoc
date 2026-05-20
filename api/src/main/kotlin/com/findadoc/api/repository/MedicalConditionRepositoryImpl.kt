package com.findadoc.api.repository

import com.findadoc.api.search.RankedTarget
import com.findadoc.api.search.SearchTargetType
import com.findadoc.api.web.dto.MedicalConditionListItemDto
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
import org.springframework.stereotype.Repository

@Repository
class MedicalConditionRepositoryImpl(
    private val dsl: DSLContext,
) : MedicalConditionRepositoryCustom {

    override fun countDoctorsBySlug(slug: String): Long = countBySlug(slug, null)

    override fun countAcceptingBySlug(slug: String): Long =
        countBySlug(slug, DSL.field("d.is_accepting_new_patients", Boolean::class.java).isTrue)

    override fun countTreatsChildrenBySlug(slug: String): Long =
        countBySlug(slug, DSL.field("d.treats_children", Boolean::class.java).isTrue)

    private fun countBySlug(slug: String, extra: Condition?): Long {
        var cond = DSL.field("mc.slug").eq(slug).and(DSL.field("d.status").eq("ACTIVE"))
        if (extra != null) cond = cond.and(extra)
        return dsl.select(DSL.countDistinct(DSL.field("d.id")))
            .from("medical_condition mc")
            .join("condition_specialty cs").on("cs.condition_id = mc.id")
            .join("doctor_specialty ds").on("ds.specialty_id = cs.specialty_id")
            .join("doctor d").on("d.id = ds.doctor_id")
            .where(cond)
            .fetchOne(0, Long::class.java) ?: 0L
    }

    override fun findAllWithDoctorCount(): List<MedicalConditionListItemDto> =
        dsl.select(
            DSL.field("mc.slug"),
            DSL.field("mc.name_ka"),
            DSL.field("mc.name_en"),
            DSL.countDistinct(DSL.field("d.id")).`as`("doctor_count"),
        )
            .from("medical_condition mc")
            .leftJoin("condition_specialty cs").on("cs.condition_id = mc.id")
            .leftJoin("doctor_specialty ds").on("ds.specialty_id = cs.specialty_id")
            .leftJoin("doctor d").on("d.id = ds.doctor_id AND d.status = 'ACTIVE'")
            .groupBy(
                DSL.field("mc.id"),
                DSL.field("mc.slug"),
                DSL.field("mc.name_ka"),
                DSL.field("mc.name_en"),
                DSL.field("mc.sort_order"),
            )
            .orderBy(DSL.field("mc.sort_order").asc(), DSL.field("mc.name_en").asc())
            .fetch { r ->
                MedicalConditionListItemDto(
                    slug = r.get("mc.slug", String::class.java),
                    nameKa = r.get("mc.name_ka", String::class.java),
                    nameEn = r.get("mc.name_en", String::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }

    override fun searchRank(q: String, threshold: Double, limit: Int): List<RankedTarget> {
        val score = DSL.field(
            "greatest(" +
                "word_similarity({0}, lower(mc.name_en)), " +
                "word_similarity({0}, lower(mc.name_ka)), " +
                "coalesce((select max(word_similarity({0}, lower(cy.term))) " +
                "from condition_synonym cy where cy.condition_id = mc.id), 0))",
            SQLDataType.DOUBLE, DSL.`val`(q),
        ).`as`("score")
        val isExact = DSL.field(
            "(lower(mc.name_en) = {0} or lower(mc.name_ka) = {0} or exists " +
                "(select 1 from condition_synonym cy where cy.condition_id = mc.id and lower(cy.term) = {0}))",
            SQLDataType.BOOLEAN, DSL.`val`(q),
        ).`as`("is_exact")
        val doctorCount = DSL.field(
            "(select count(distinct d.id) from condition_specialty cs " +
                "join doctor_specialty ds on ds.specialty_id = cs.specialty_id " +
                "join doctor d on d.id = ds.doctor_id " +
                "where cs.condition_id = mc.id and d.status = 'ACTIVE')",
            SQLDataType.BIGINT,
        ).`as`("doctor_count")
        val matches = DSL.condition(
            "(word_similarity({0}, lower(mc.name_en)) > {1} or word_similarity({0}, lower(mc.name_ka)) > {1} " +
                "or exists (select 1 from condition_synonym cy where cy.condition_id = mc.id " +
                "and word_similarity({0}, lower(cy.term)) > {1}))",
            DSL.`val`(q), DSL.`val`(threshold),
        )
        return dsl.select(DSL.field("mc.slug"), DSL.field("mc.name_en"), DSL.field("mc.name_ka"), score, isExact, doctorCount)
            .from("medical_condition mc")
            .where(matches)
            .orderBy(DSL.field("is_exact").desc(), DSL.field("score").desc(), DSL.field("doctor_count").desc())
            .limit(limit)
            .fetch { r ->
                RankedTarget(
                    type = SearchTargetType.CONDITION,
                    slug = r.get("mc.slug", String::class.java),
                    nameEn = r.get("mc.name_en", String::class.java),
                    nameKa = r.get("mc.name_ka", String::class.java),
                    score = r.get("score", Double::class.java),
                    exact = r.get("is_exact", Boolean::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }
    }
}
