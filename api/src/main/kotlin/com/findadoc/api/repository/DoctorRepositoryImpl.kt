package com.findadoc.api.repository

import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.repository.jooq.doctorConditions
import com.findadoc.api.repository.jooq.relevance
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.SpecialtyRefDto
import org.jooq.DSLContext
import org.jooq.SortField
import org.jooq.impl.DSL
import org.springframework.data.domain.Page
import org.springframework.data.domain.PageImpl
import org.springframework.data.domain.Pageable
import org.springframework.stereotype.Repository

@Repository
class DoctorRepositoryImpl(
    private val dsl: DSLContext,
) : DoctorRepositoryCustom {

    override fun findFiltered(filter: DoctorFilter, sort: String?, pageable: Pageable): Page<DoctorListItemDto> {
        val conditions = doctorConditions(filter)

        val records = dsl.select(
            DSL.field("d.slug"),
            DSL.field("d.full_name_ka"),
            DSL.field("d.full_name_en"),
            DSL.field("d.photo_url"),
            DSL.field("d.is_accepting_new_patients"),
            DSL.field("d.treats_children"),
            DSL.field("d.treats_adults"),
            DSL.field("d.specialty_ka"),
            DSL.field("d.specialty_en"),
            DSL.field("ps.slug").`as`("ps_slug"),
            DSL.field("ps.name_ka").`as`("ps_name_ka"),
            DSL.field("ps.name_en").`as`("ps_name_en"),
        )
            .from("doctor d")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .leftJoin("doctor_specialty dsp").on("dsp.doctor_id = d.id AND dsp.is_primary = true")
            .leftJoin("specialty ps").on("ps.id = dsp.specialty_id")
            .where(conditions)
            .orderBy(orderBy(filter, sort))
            .limit(pageable.pageSize)
            .offset(pageable.offset)
            .fetch { r ->
                val psSlug = r.get("ps_slug", String::class.java)
                DoctorListItemDto(
                    slug = r.get("d.slug", String::class.java),
                    fullNameKa = r.get("d.full_name_ka", String::class.java),
                    fullNameEn = r.get("d.full_name_en", String::class.java),
                    photoUrl = r.get("d.photo_url", String::class.java),
                    isAcceptingNewPatients = r.get("d.is_accepting_new_patients", Boolean::class.java),
                    treatsChildren = r.get("d.treats_children", Boolean::class.java),
                    treatsAdults = r.get("d.treats_adults", Boolean::class.java),
                    specialtyKa = r.get("d.specialty_ka", String::class.java),
                    specialtyEn = r.get("d.specialty_en", String::class.java),
                    primarySpecialty = psSlug?.let {
                        SpecialtyRefDto(
                            slug = it,
                            nameKa = r.get("ps_name_ka", String::class.java),
                            nameEn = r.get("ps_name_en", String::class.java),
                        )
                    },
                )
            }

        val total = dsl.selectCount()
            .from("doctor d")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .where(conditions)
            .fetchOne(0, Long::class.java) ?: 0L

        return PageImpl(records, pageable, total)
    }

    private fun orderBy(filter: DoctorFilter, sort: String?): List<SortField<*>> = buildList {
        val q = filter.q?.takeIf { it.isNotEmpty() }
        if (q != null && (sort == "relevancy" || sort == null)) {
            add(relevance(q).desc())
        }
        val familyName = DSL.field("d.family_name_en")
        add(if (sort == "ztoa") familyName.desc() else familyName.asc())
        add(DSL.field("d.slug").asc())
    }
}
