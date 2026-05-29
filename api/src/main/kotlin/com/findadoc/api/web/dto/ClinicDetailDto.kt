package com.findadoc.api.web.dto

data class ClinicDetailDto(
    val slug: String,
    val nameKa: String,
    val nameEn: String,
    val address: String?,
    val addressEn: String?,
    val phone: String?,
    val website: String?,
    val lat: Double?,
    val lng: Double?,
    val doctorCount: Long,
    val brand: ClinicBrandRefDto?,
    val branches: List<ClinicBranchDto>,
)
