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
)
