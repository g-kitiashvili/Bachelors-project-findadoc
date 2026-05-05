package com.findadoc.api.web.dto

data class ClinicDetailDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val address: String?,
    val phone: String?,
    val website: String?,
    val doctorCount: Long,
)
