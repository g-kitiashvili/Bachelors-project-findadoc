package com.findadoc.api.web

import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.web.dto.DoctorListItemDto
import com.findadoc.api.web.dto.DoctorProfileDto
import com.findadoc.api.web.dto.PageResponseDto
import com.findadoc.api.web.dto.toListItemDto
import com.findadoc.api.web.dto.toProfileDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.data.domain.PageRequest
import org.springframework.data.domain.Sort
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/doctors")
@Tag(name = "Doctors", description = "Read access to scraped doctor records.")
class DoctorController(
    private val doctorRepository: DoctorRepository,
) {
    @Operation(summary = "List doctors")
    @GetMapping
    fun getAll(
        @RequestParam(defaultValue = "1") page: Int,
        @RequestParam(defaultValue = "5") pageSize: Int,
    ): PageResponseDto<DoctorListItemDto> {
        val safePage = maxOf(page, 1)
        val safePageSize = pageSize.coerceIn(1, 50)
        val sort = Sort.by("fullNameEn", "slug")
        val result = doctorRepository.findByStatus(
            status = "ACTIVE",
            pageable = PageRequest.of(safePage - 1, safePageSize, sort),
        )
        return PageResponseDto(
            items = result.content.map { it.toListItemDto() },
            page = safePage,
            pageSize = safePageSize,
            total = result.totalElements,
        )
    }

    @Operation(summary = "Get a doctor by slug")
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): DoctorProfileDto {
        val doctor = doctorRepository.findBySlug(slug)
            ?: throw DoctorNotFoundException(slug)
        return doctor.toProfileDto()
    }
}
