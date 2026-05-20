package com.findadoc.api.search

data class RankedTarget(
    val type: SearchTargetType,
    val slug: String,
    val nameEn: String,
    val nameKa: String,
    val score: Double,
    val exact: Boolean,
    val doctorCount: Long,
)
