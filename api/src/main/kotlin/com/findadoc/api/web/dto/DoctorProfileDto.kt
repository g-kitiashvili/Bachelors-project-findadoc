package com.findadoc.api.web.dto

import com.findadoc.api.domain.Doctor

data class DoctorProfileDto(
    val slug: String,
    val fullNameKa: String,
    val fullNameEn: String,
    val gender: String?,
    val photoUrl: String?,
    val isAcceptingNewPatients: Boolean,
    val treatsChildren: Boolean,
    val treatsAdults: Boolean,
    val bioKa: String?,
    val bioEn: String?,
    val specialtyKa: String?,
    val specialtyEn: String?,
    val specialties: List<SpecialtyRefWithFlagDto>,
    val clinics: List<ClinicRefDto>,
)

fun Doctor.toProfileDto(): DoctorProfileDto = DoctorProfileDto(
    slug = slug,
    fullNameKa = fullNameKa,
    fullNameEn = fullNameEn,
    gender = gender,
    photoUrl = photoUrl,
    isAcceptingNewPatients = isAcceptingNewPatients,
    treatsChildren = treatsChildren,
    treatsAdults = treatsAdults,
    bioKa = bioKa,
    bioEn = bioEn,
    specialtyKa = specialtyKa,
    specialtyEn = specialtyEn,
    specialties = doctorSpecialties
        .sortedWith(compareByDescending<com.findadoc.api.domain.DoctorSpecialty> { it.isPrimary }
            .thenBy { it.specialty.sortOrder })
        .map { SpecialtyRefWithFlagDto(
            slug = it.specialty.slug,
            nameKa = it.specialty.nameKa,
            nameEn = it.specialty.nameEn,
            isPrimary = it.isPrimary,
        ) },
    clinics = doctorClinics
        .map { it.clinic }
        .filter { it.status == "ACTIVE" }
        .sortedBy { it.nameEn }
        .map { ClinicRefDto(slug = it.slug, nameKa = it.nameKa, nameEn = it.nameEn, address = it.address, addressEn = it.addressEn) },
)
