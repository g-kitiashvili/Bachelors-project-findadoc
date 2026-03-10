package com.findadoc.api.web

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
}
