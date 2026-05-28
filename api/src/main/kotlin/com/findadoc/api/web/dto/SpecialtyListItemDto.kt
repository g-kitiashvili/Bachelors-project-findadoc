package com.findadoc.api.web.dto

data class SpecialtyListItemDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val doctorCount: Long,
    val parentSlug: String? = null,
)
