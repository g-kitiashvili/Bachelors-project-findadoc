package com.findadoc.api.web

import com.findadoc.api.service.ClinicNotFoundException
import com.findadoc.api.service.DoctorNotFoundException
import com.findadoc.api.service.MedicalConditionNotFoundException
import com.findadoc.api.service.SpecialtyNotFoundException
import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.web.bind.annotation.ControllerAdvice
import org.springframework.web.bind.annotation.ExceptionHandler
import java.net.URI

@ControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(DoctorNotFoundException::class)
    fun handleDoctorNotFound(ex: DoctorNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "Doctor with slug '${ex.slug}' not found",
        ).apply {
            type = URI.create("https://findadoc.example.com/problems/doctor-not-found")
            title = "Doctor not found"
            setProperty("slug", ex.slug)
        }

    @ExceptionHandler(ClinicNotFoundException::class)
    fun handleClinicNotFound(ex: ClinicNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "Clinic with slug '${ex.slug}' not found",
        ).apply {
            type = URI.create("https://findadoc.example.com/problems/clinic-not-found")
            title = "Clinic not found"
            setProperty("slug", ex.slug)
        }

    @ExceptionHandler(SpecialtyNotFoundException::class)
    fun handleSpecialtyNotFound(ex: SpecialtyNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "Specialty with slug '${ex.slug}' not found",
        ).apply {
            type = URI.create("https://findadoc.example.com/problems/specialty-not-found")
            title = "Specialty not found"
            setProperty("slug", ex.slug)
        }

    @ExceptionHandler(MedicalConditionNotFoundException::class)
    fun handleMedicalConditionNotFound(ex: MedicalConditionNotFoundException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "Medical condition with slug '${ex.slug}' not found",
        ).apply {
            type = URI.create("https://findadoc.example.com/problems/medical-condition-not-found")
            title = "Medical condition not found"
            setProperty("slug", ex.slug)
        }
}
