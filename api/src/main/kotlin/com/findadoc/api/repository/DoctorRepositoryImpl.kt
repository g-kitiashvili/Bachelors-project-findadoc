package com.findadoc.api.repository

import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.repository.jooq.doctorConditions
import com.findadoc.api.repository.jooq.nameRelevance
import com.findadoc.api.repository.jooq.relevance
import com.findadoc.api.web.dto.ClinicRefDto
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.MapPinDto
import com.findadoc.api.web.dto.SpecialtyRefDto
import org.jooq.Condition
import org.jooq.DSLContext
import org.jooq.SortField
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType
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
            DSL.field("(select c.slug from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_slug"),
            DSL.field("(select c.name_ka from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_name_ka"),
            DSL.field("(select c.name_en from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_name_en"),
            DSL.field("(select c.address from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_address"),
            DSL.field("(select c.address_en from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_address_en"),
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
                val pcSlug = r.get("pc_slug", String::class.java)
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
                    primaryClinic = pcSlug?.let {
                        ClinicRefDto(
                            slug = it,
                            nameKa = r.get("pc_name_ka", String::class.java),
                            nameEn = r.get("pc_name_en", String::class.java),
                            address = r.get("pc_address", String::class.java),
                            addressEn = r.get("pc_address_en", String::class.java),
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

    override fun mapPins(filter: DoctorFilter, centerLat: Double?, centerLng: Double?, radiusKm: Double?): List<MapPinDto> {
        // The clinic facet picks which pins to show, not merely which doctors qualify. Constrain the
        // projected clinic to the selected slugs (and drop the now-redundant doctor-level EXISTS) so a
        // clinic filter can't fan out to pins for the matching doctors' other workplaces.
        val filterByClinic = filter.clinicSlugs.isNotEmpty()
        val conditions: MutableList<Condition> = doctorConditions(filter, excludeClinic = filterByClinic).toMutableList()
        conditions.add(DSL.field("c.status").eq("ACTIVE"))
        conditions.add(DSL.field("c.location").isNotNull)
        if (filterByClinic) {
            conditions.add(DSL.field("c.slug").`in`(filter.clinicSlugs))
        }
        if (centerLat != null && centerLng != null && radiusKm != null) {
            conditions.add(
                DSL.condition(
                    "ST_DWithin(c.location, ST_MakePoint({0}, {1})::geography, {2})",
                    DSL.`val`(centerLng), DSL.`val`(centerLat), DSL.`val`(radiusKm * 1000.0),
                ),
            )
        }
        return dsl.select(
            DSL.field("c.slug"),
            DSL.field("c.name_ka"),
            DSL.field("c.name_en"),
            DSL.field("ST_Y(c.location::geometry)", SQLDataType.DOUBLE).`as`("lat"),
            DSL.field("ST_X(c.location::geometry)", SQLDataType.DOUBLE).`as`("lng"),
            DSL.countDistinct(DSL.field("d.id")).`as`("docs"),
        )
            .from("doctor d")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .join("doctor_clinic dc").on("dc.doctor_id = d.id")
            .join("clinic c").on("c.id = dc.clinic_id")
            .where(conditions)
            .groupBy(
                DSL.field("c.id"), DSL.field("c.slug"), DSL.field("c.name_ka"),
                DSL.field("c.name_en"), DSL.field("c.location"),
            )
            .fetch { r ->
                MapPinDto(
                    slug = r.get("c.slug", String::class.java),
                    nameKa = r.get("c.name_ka", String::class.java),
                    nameEn = r.get("c.name_en", String::class.java),
                    lat = r.get("lat", Double::class.java),
                    lng = r.get("lng", Double::class.java),
                    doctorCount = r.get("docs", Long::class.java),
                )
            }
    }

    // Same-specialty peers, ranked by shared-specialty count, then proximity (shared clinic >
    // same city > same region), then profile completeness.
    override fun findSimilar(slug: String, limit: Int): List<DoctorListItemDto> {
        val sharedSpecialties = DSL.field(
            "(select count(distinct sx.specialty_id) from doctor_specialty sx where sx.doctor_id = d.id " +
                "and sx.specialty_id in (select sy.specialty_id from doctor_specialty sy where sy.doctor_id = td.id))",
            SQLDataType.INTEGER,
        )
        val geoScore = DSL.field(
            "case " +
                "when exists (select 1 from doctor_clinic cx join doctor_clinic cy on cy.clinic_id = cx.clinic_id " +
                "where cx.doctor_id = d.id and cy.doctor_id = td.id) then 3 " +
                "when d.location_id is not null and d.location_id = td.location_id then 2 " +
                "when loc.parent_id is not null and loc.parent_id = tloc.parent_id then 1 " +
                "else 0 end",
            SQLDataType.INTEGER,
        )
        return dsl.select(
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
            DSL.field("(select c.slug from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_slug"),
            DSL.field("(select c.name_ka from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_name_ka"),
            DSL.field("(select c.name_en from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_name_en"),
            DSL.field("(select c.address from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_address"),
            DSL.field("(select c.address_en from doctor_clinic dc join clinic c on c.id = dc.clinic_id where dc.doctor_id = d.id and c.status = 'ACTIVE' order by c.name_en asc limit 1)").`as`("pc_address_en"),
        )
            .from("doctor d")
            .join("doctor td").on(DSL.condition("td.slug = {0}", DSL.`val`(slug)))
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location tloc").on("tloc.id = td.location_id")
            .leftJoin("doctor_specialty dsp").on("dsp.doctor_id = d.id AND dsp.is_primary = true")
            .leftJoin("specialty ps").on("ps.id = dsp.specialty_id")
            .where(
                DSL.field("d.status").eq("ACTIVE"),
                DSL.condition("d.merged_into_id is null"),
                DSL.condition("d.id <> td.id"),
                DSL.condition(
                    "exists (select 1 from doctor_specialty s1 join doctor_specialty s2 " +
                        "on s2.specialty_id = s1.specialty_id where s1.doctor_id = d.id and s2.doctor_id = td.id)",
                ),
            )
            .orderBy(
                sharedSpecialties.desc(),
                geoScore.desc(),
                DSL.field("(d.photo_url is not null)", SQLDataType.BOOLEAN).desc(),
                DSL.field("d.family_name_en").asc(),
                DSL.field("d.slug").asc(),
            )
            .limit(limit)
            .fetch { r ->
                val psSlug = r.get("ps_slug", String::class.java)
                val pcSlug = r.get("pc_slug", String::class.java)
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
                    primaryClinic = pcSlug?.let {
                        ClinicRefDto(
                            slug = it,
                            nameKa = r.get("pc_name_ka", String::class.java),
                            nameEn = r.get("pc_name_en", String::class.java),
                            address = r.get("pc_address", String::class.java),
                            addressEn = r.get("pc_address_en", String::class.java),
                        )
                    },
                )
            }
    }

    private fun orderBy(filter: DoctorFilter, sort: String?): List<SortField<*>> = buildList {
        val q = filter.q?.takeIf { it.isNotEmpty() }
        // prominence drives the default browse order and breaks ties in relevance search,
        // but yields to an explicit alphabetical choice (atoz/ztoa).
        val byProminence = sort == null || sort == "relevancy"
        if (q != null && byProminence) {
            add((if (filter.nameOnly) nameRelevance(q) else relevance(q)).desc())
        }
        if (byProminence) {
            add(DSL.field("d.prominence").desc())
        }
        val familyName = DSL.field("d.family_name_en")
        add(if (sort == "ztoa") familyName.desc() else familyName.asc())
        add(DSL.field("d.slug").asc())
    }
}
