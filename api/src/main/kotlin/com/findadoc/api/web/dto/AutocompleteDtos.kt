package com.findadoc.api.web.dto

import com.findadoc.api.domain.Doctor
import com.findadoc.api.domain.Specialty

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

fun Doctor.toSuggestionDto() = DoctorSuggestionDto(
    slug = slug,
    fullNameEn = fullNameEn,
    fullNameKa = fullNameKa,
    primarySpecialtyEn = doctorSpecialties.firstOrNull { it.isPrimary }?.specialty?.nameEn,
)

fun Specialty.toSuggestionDto() = SpecialtySuggestionDto(
    slug = slug,
    nameEn = nameEn,
    nameKa = nameKa,
)
