package com.findadoc.api.web.dto

import com.findadoc.api.domain.Doctor

data class DoctorListItemDto(
    val slug: String,
    val fullNameKa: String,
    val fullNameEn: String,
    val photoUrl: String?,
    val isAcceptingNewPatients: Boolean,
    val treatsChildren: Boolean,
    val treatsAdults: Boolean,
)

fun Doctor.toListItemDto(): DoctorListItemDto = DoctorListItemDto(
    slug = slug,
    fullNameKa = fullNameKa,
    fullNameEn = fullNameEn,
    photoUrl = photoUrl,
    isAcceptingNewPatients = isAcceptingNewPatients,
    treatsChildren = treatsChildren,
    treatsAdults = treatsAdults,
)
