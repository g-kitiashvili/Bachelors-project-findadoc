package com.findadoc.api.web.dto

data class SearchResolutionDto(
    val type: String,
    val slug: String?,
    val label: String,
)
