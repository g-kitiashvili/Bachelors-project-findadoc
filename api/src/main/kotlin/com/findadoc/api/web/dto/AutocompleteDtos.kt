package com.findadoc.api.web.dto

data class AutocompleteResponseDto(
    val doctors: List<DoctorSuggestionDto>,
    val specialties: List<SpecialtySuggestionDto>,
)

data class DoctorSuggestionDto(
    val slug: String,
    val fullNameEn: String,
    val fullNameKa: String,
    val primarySpecialtyEn: String?,
)

data class SpecialtySuggestionDto(
    val slug: String,
    val nameEn: String,
    val nameKa: String,
)

fun DoctorListItemDto.toSuggestionDto() = DoctorSuggestionDto(
    slug = slug,
    fullNameEn = fullNameEn,
    fullNameKa = fullNameKa,
    primarySpecialtyEn = primarySpecialty?.nameEn,
)
