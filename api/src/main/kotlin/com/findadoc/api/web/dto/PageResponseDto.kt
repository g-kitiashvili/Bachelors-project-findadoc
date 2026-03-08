package com.findadoc.api.web.dto

data class PageResponseDto<T>(
    val items: List<T>,
    val page: Int,
    val pageSize: Int,
    val total: Long,
)
