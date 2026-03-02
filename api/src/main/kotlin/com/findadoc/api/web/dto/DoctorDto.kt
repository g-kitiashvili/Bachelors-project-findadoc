package com.findadoc.api.web.dto

import com.findadoc.api.domain.Doctor

data class DoctorDto(
    val slug: String,
    val fullName: String,
)

fun Doctor.toDto(): DoctorDto = DoctorDto(
    slug = slug,
    fullName = fullName,
)
