package com.findadoc.api.web.dto

data class ClinicBranchDto(
    val slug: String,
    val nameEn: String,
    val nameKa: String,
    val address: String?,
    val located: Boolean,
)
