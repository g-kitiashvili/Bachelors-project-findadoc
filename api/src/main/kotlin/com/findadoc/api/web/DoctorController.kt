package com.findadoc.api.web

import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.web.dto.DoctorDto
import com.findadoc.api.web.dto.toDto
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/doctors")
class DoctorController(
    private val doctorRepository: DoctorRepository,
) {
    @GetMapping("/{slug}")
    fun getBySlug(@PathVariable slug: String): ResponseEntity<DoctorDto> {
        val doctor = doctorRepository.findBySlug(slug)
            ?: return ResponseEntity.notFound().build()
        return ResponseEntity.ok(doctor.toDto())
    }
}
