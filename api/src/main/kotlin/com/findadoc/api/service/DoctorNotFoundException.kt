package com.findadoc.api.service

class DoctorNotFoundException(val slug: String) : RuntimeException("Doctor not found: $slug")
