package com.findadoc.api.web.dto

data class MedicalConditionDetailDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val descriptionKa: String?,
    val descriptionEn: String?,
    val doctorCount: Long,
    val acceptingCount: Long,
    val treatsChildrenCount: Long,
)
