package com.findadoc.api.web.request

/** Trim entries and drop blanks from a multi-value query param bound as a list. */
private fun List<String>.normalizedSlugs(): List<String> = map(String::trim).filter { it.isNotEmpty() }

/** Trim and null out a blank string field. */
private fun String?.cleaned(): String? = this?.trim()?.takeIf { it.isNotEmpty() }

/**
 * Spring command objects for the GET search/list endpoints. Bound via @ModelAttribute:
 * scalar params bind by name, and multi-value filters are real `List<String>` properties
 * that Spring fills from repeated query params (`?specialty=a&specialty=b`) - no
 * comma-splitting. The accessor methods centralize the trim/coerce/whitelist normalization.
 */
open class AgeGroupParams {
    var treatsChildren: Boolean = false
    var treatsAdults: Boolean = false
}

/** Facets shared by the doctor list and the clinic map (same doctor query surface). */
open class DoctorFacetParams : AgeGroupParams() {
    var q: String? = null
    var specialty: List<String> = emptyList()
    var region: String? = null
    var city: String? = null
    var clinic: List<String> = emptyList()
    var condition: List<String> = emptyList()

    fun query(): String? = q?.trim()?.take(100)?.takeIf { it.isNotEmpty() }
    fun specialtySlugs(): List<String> = specialty.normalizedSlugs()
    fun clinicSlugs(): List<String> = clinic.normalizedSlugs()
    fun conditionSlugs(): List<String> = condition.normalizedSlugs()
    fun regionSlug(): String? = region.cleaned()
    fun citySlug(): String? = city.cleaned()
}

class DoctorListParams : DoctorFacetParams() {
    var sort: String? = null
    var page: Int = 1
    var pageSize: Int = 5

    fun safePage(): Int = maxOf(page, 1)
    fun safePageSize(): Int = pageSize.coerceIn(1, 50)
    fun sortMode(): String? =
        sort?.trim()?.lowercase()?.takeIf { it == "relevancy" || it == "atoz" || it == "ztoa" }
}

class MapPinsParams : DoctorFacetParams() {
    var center: String? = null
    var radiusKm: Double? = null

    private fun centerPart(i: Int): Double? = center?.split(',')?.getOrNull(i)?.trim()?.toDoubleOrNull()
    fun lat(): Double? = centerPart(0)
    fun lng(): Double? = centerPart(1)
}

class ClinicListParams : AgeGroupParams() {
    var q: String? = null
    var region: String? = null
    var city: String? = null
    var specialty: List<String> = emptyList()
    var located: Boolean = false
    var collapse: Boolean = false
    var page: Int = 1
    var pageSize: Int = 50

    fun query(): String? = q.cleaned()
    fun regionSlug(): String? = region.cleaned()
    fun citySlug(): String? = city.cleaned()
    fun specialtySlugs(): List<String> = specialty.normalizedSlugs()
    fun safePage(): Int = maxOf(page, 1)
    fun safePageSize(): Int = pageSize.coerceIn(1, 500)
}

class SpecialtyListParams : AgeGroupParams() {
    var region: String? = null
    var city: String? = null
    var clinic: List<String> = emptyList()

    fun regionSlug(): String? = region.cleaned()
    fun citySlug(): String? = city.cleaned()
    fun clinicSlugs(): List<String> = clinic.normalizedSlugs()
}

class LocationListParams : AgeGroupParams() {
    var specialty: List<String> = emptyList()
    var clinic: List<String> = emptyList()

    fun specialtySlugs(): List<String> = specialty.normalizedSlugs()
    fun clinicSlugs(): List<String> = clinic.normalizedSlugs()
}
