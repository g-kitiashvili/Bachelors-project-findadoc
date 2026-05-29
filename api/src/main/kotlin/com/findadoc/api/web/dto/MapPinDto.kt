package com.findadoc.api.web.dto

data class MapPinDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val lat: Double,
    val lng: Double,
    val doctorCount: Long,
)
