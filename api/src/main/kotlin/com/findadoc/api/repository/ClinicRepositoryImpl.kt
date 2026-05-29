package com.findadoc.api.repository

import com.findadoc.api.repository.jooq.FUZZY_THRESHOLD
import com.findadoc.api.web.dto.ClinicBranchDto
import com.findadoc.api.web.dto.ClinicBrandRefDto
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
        located: Boolean,
        collapseBrands: Boolean,
        limit: Int,
        offset: Int,
    ): List<ClinicListItemDto> {
        if (collapseBrands) return facetCollapsed(q, limit, offset)
        val conditions = mutableListOf<Condition>(
            DSL.field("c.status").eq("ACTIVE"),
            DSL.field("d.status").eq("ACTIVE"),
        )
        if (located) conditions += DSL.field("c.location").isNotNull
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
            .offset(offset)
            .fetch { r ->
                ClinicListItemDto(
                    slug = r.get("c.slug", String::class.java),
                    nameKa = r.get("c.name_ka", String::class.java),
                    nameEn = r.get("c.name_en", String::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                )
            }
    }

    override fun countFacet(q: String?, region: String?, city: String?, specialtySlugs: List<String>, located: Boolean, collapseBrands: Boolean): Long {
        if (collapseBrands) return countFacetCollapsed(q)
        val conditions = mutableListOf<Condition>(
            DSL.field("c.status").eq("ACTIVE"),
            DSL.field("d.status").eq("ACTIVE"),
        )
        if (located) conditions += DSL.field("c.location").isNotNull
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
        return dsl.select(DSL.countDistinct(DSL.field("c.id")))
            .from("clinic c")
            .join("doctor_clinic dc").on("dc.clinic_id = c.id")
            .join("doctor d").on("d.id = dc.doctor_id")
            .leftJoin("location loc").on("loc.id = d.location_id")
            .leftJoin("location reg").on("reg.id = loc.parent_id")
            .where(conditions)
            .fetchOne(0, Long::class.java) ?: 0L
    }

    private fun collapsedConditions(q: String?): MutableList<Condition> {
        val conditions = mutableListOf<Condition>(
            DSL.field("c.status").eq("ACTIVE"),
            DSL.field("d.status").eq("ACTIVE"),
        )
        q?.takeIf { it.isNotEmpty() }?.let {
            conditions += DSL.greatest(
                DSL.field("word_similarity({0}, lower(coalesce(cb.name_en, c.name_en)))", SQLDataType.DOUBLE, DSL.`val`(it)),
                DSL.field("word_similarity({0}, coalesce(cb.name_ka, c.name_ka))", SQLDataType.DOUBLE, DSL.`val`(it)),
            ).gt(FUZZY_THRESHOLD)
        }
        return conditions
    }

    // One row per brand (branded clinics collapse to their brand; unbranded stay per-clinic),
    // with the brand's branches embedded so the browse UI can expand them inline.
    private fun facetCollapsed(q: String?, limit: Int, offset: Int): List<ClinicListItemDto> {
        val rows = dsl.select(
            DSL.field("coalesce(max(cb.slug), min(c.slug))").`as`("slug"),
            DSL.field("coalesce(max(cb.name_ka), min(c.name_ka))").`as`("name_ka"),
            DSL.field("coalesce(max(cb.name_en), min(c.name_en))").`as`("name_en"),
            DSL.countDistinct(DSL.field("d.id")).`as`("doctor_count"),
            DSL.field("max(cb.slug)").`as`("brand_slug"),
        )
            .from("clinic c")
            .join("doctor_clinic dc").on("dc.clinic_id = c.id")
            .join("doctor d").on("d.id = dc.doctor_id")
            .leftJoin("clinic_brand cb").on("cb.id = c.brand_id")
            .where(collapsedConditions(q))
            .groupBy(DSL.field("coalesce('b' || c.brand_id::text, 'c' || c.id::text)"))
            .orderBy(
                DSL.countDistinct(DSL.field("d.id")).desc(),
                DSL.field("coalesce(max(cb.name_en), min(c.name_en))").asc(),
            )
            .limit(limit).offset(offset)
            .fetch { r ->
                CollapsedRow(
                    slug = r.get("slug", String::class.java),
                    nameKa = r.get("name_ka", String::class.java),
                    nameEn = r.get("name_en", String::class.java),
                    doctorCount = r.get("doctor_count", Long::class.java),
                    brandSlug = r.get("brand_slug", String::class.java),
                )
            }
        val brandSlugs = rows.mapNotNull { it.brandSlug }.distinct()
        val branchesByBrand = if (brandSlugs.isEmpty()) emptyMap() else branchesForBrands(brandSlugs)
        return rows.map { row ->
            ClinicListItemDto(row.slug, row.nameKa, row.nameEn, row.doctorCount, row.brandSlug?.let { branchesByBrand[it] })
        }
    }

    private fun branchesForBrands(brandSlugs: List<String>): Map<String, List<ClinicBranchDto>> =
        dsl.select(
            DSL.field("cb.slug").`as`("brand_slug"),
            DSL.field("c.slug").`as`("slug"),
            DSL.field("c.name_en").`as`("name_en"),
            DSL.field("c.name_ka").`as`("name_ka"),
            DSL.field("c.address").`as`("address"),
            DSL.field("c.location IS NOT NULL", Boolean::class.java).`as`("located"),
        )
            .from("clinic c")
            .join("clinic_brand cb").on("cb.id = c.brand_id")
            .where(DSL.field("cb.slug").`in`(brandSlugs).and(DSL.field("c.status").eq("ACTIVE")))
            .orderBy(DSL.field("c.name_en").asc())
            .fetchGroups(
                { it.get("brand_slug", String::class.java) },
                { r ->
                    ClinicBranchDto(
                        slug = r.get("slug", String::class.java),
                        nameEn = r.get("name_en", String::class.java),
                        nameKa = r.get("name_ka", String::class.java),
                        address = r.get("address", String::class.java),
                        located = r.get("located", Boolean::class.java),
                    )
                },
            )

    private fun countFacetCollapsed(q: String?): Long =
        dsl.select(DSL.countDistinct(DSL.field("coalesce('b' || c.brand_id::text, 'c' || c.id::text)")))
            .from("clinic c")
            .join("doctor_clinic dc").on("dc.clinic_id = c.id")
            .join("doctor d").on("d.id = dc.doctor_id")
            .leftJoin("clinic_brand cb").on("cb.id = c.brand_id")
            .where(collapsedConditions(q))
            .fetchOne(0, Long::class.java) ?: 0L

    override fun coordinatesBySlug(slug: String): Pair<Double, Double>? =
        dsl.select(
            DSL.field("ST_Y(location::geometry)", SQLDataType.DOUBLE).`as`("lat"),
            DSL.field("ST_X(location::geometry)", SQLDataType.DOUBLE).`as`("lng"),
        )
            .from("clinic")
            .where(DSL.field("slug").eq(slug).and(DSL.field("location").isNotNull))
            .fetchOne()
            ?.let { it.get("lat", Double::class.java) to it.get("lng", Double::class.java) }

    override fun brandBySlug(slug: String): ClinicBrandRefDto? =
        dsl.select(DSL.field("cb.slug"), DSL.field("cb.name_en"), DSL.field("cb.name_ka"))
            .from("clinic c")
            .join("clinic_brand cb").on("cb.id = c.brand_id")
            .where(DSL.field("c.slug").eq(slug))
            .fetchOne()
            ?.let {
                ClinicBrandRefDto(
                    slug = it.get("cb.slug", String::class.java),
                    nameEn = it.get("cb.name_en", String::class.java),
                    nameKa = it.get("cb.name_ka", String::class.java),
                )
            }

    override fun branchesBySlug(slug: String): List<ClinicBranchDto> =
        dsl.select(
            DSL.field("s.slug"),
            DSL.field("s.name_en"),
            DSL.field("s.name_ka"),
            DSL.field("s.address"),
            DSL.field("s.location IS NOT NULL", Boolean::class.java).`as`("located"),
        )
            .from("clinic c")
            .join("clinic s").on("s.brand_id = c.brand_id")
            .where(
                DSL.field("c.slug").eq(slug)
                    .and(DSL.field("c.brand_id").isNotNull)
                    .and(DSL.field("s.id").ne(DSL.field("c.id")))
                    .and(DSL.field("s.status").eq("ACTIVE")),
            )
            .orderBy(DSL.field("s.name_en").asc())
            .fetch { r ->
                ClinicBranchDto(
                    slug = r.get("s.slug", String::class.java),
                    nameEn = r.get("s.name_en", String::class.java),
                    nameKa = r.get("s.name_ka", String::class.java),
                    address = r.get("s.address", String::class.java),
                    located = r.get("located", Boolean::class.java),
                )
            }

    override fun countDoctorsBySlug(slug: String): Long =
        dsl.selectCount().from("doctor_clinic dc").join("clinic c").on("c.id = dc.clinic_id").join("doctor d").on("d.id = dc.doctor_id")
            .where(DSL.field("c.slug").eq(slug).and(DSL.field("c.status").eq("ACTIVE")).and(DSL.field("d.status").eq("ACTIVE")))
            .fetchOne(0, Long::class.java) ?: 0L

    override fun autocomplete(q: String, threshold: Double, limit: Int): List<ClinicSuggestionDto> {
        val sim = DSL.greatest(
            DSL.field("word_similarity({0}, lower(c.name_en))", SQLDataType.DOUBLE, DSL.`val`(q)),
            DSL.field("word_similarity({0}, c.name_ka)", SQLDataType.DOUBLE, DSL.`val`(q)),
        )
        return dsl.select(DSL.field("c.slug"), DSL.field("c.name_en"), DSL.field("c.name_ka"))
            .from("clinic c")
            .where(DSL.field("c.status").eq("ACTIVE").and(sim.gt(threshold)))
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

private data class CollapsedRow(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val doctorCount: Long,
    val brandSlug: String?,
)
