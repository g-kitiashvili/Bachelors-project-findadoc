package com.findadoc.api.web.dto

data class MedicalConditionListItemDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val doctorCount: Long,
)
