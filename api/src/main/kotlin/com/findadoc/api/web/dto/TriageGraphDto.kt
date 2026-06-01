package com.findadoc.api.web.dto

data class LocalizedTextDto(val ka: String, val en: String)

data class TriageResultDto(val type: String, val slug: String)

data class TriageOptionDto(
    val label: LocalizedTextDto,
    val next: String? = null,
    val result: TriageResultDto? = null,
)

data class TriageSymptomDto(
    val label: LocalizedTextDto,
    val weights: Map<String, Int> = emptyMap(),
)

data class TriageNodeDto(
    val question: LocalizedTextDto,
    val options: List<TriageOptionDto> = emptyList(),
    val symptoms: List<TriageSymptomDto>? = null,
)

data class TriageGraphDto(
    val start: String,
    val nodes: Map<String, TriageNodeDto>,
)
