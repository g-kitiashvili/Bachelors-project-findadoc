package com.findadoc.api.repository

import com.findadoc.api.web.dto.MedicalConditionListItemDto
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.impl.DSL
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
}
