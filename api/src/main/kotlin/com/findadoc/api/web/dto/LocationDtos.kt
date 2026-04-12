package com.findadoc.api.web.dto

data class LocationCityDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val doctorCount: Long,
)

data class LocationRegionDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val doctorCount: Long,
    val cities: List<LocationCityDto>,
)
