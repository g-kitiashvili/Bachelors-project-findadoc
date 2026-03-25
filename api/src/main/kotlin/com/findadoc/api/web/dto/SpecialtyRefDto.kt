package com.findadoc.api.web.dto

import com.findadoc.api.domain.Specialty

data class SpecialtyRefDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
)

data class SpecialtyRefWithFlagDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val isPrimary: Boolean,
)

fun Specialty.toRefDto() = SpecialtyRefDto(slug = slug, nameKa = nameKa, nameEn = nameEn)
