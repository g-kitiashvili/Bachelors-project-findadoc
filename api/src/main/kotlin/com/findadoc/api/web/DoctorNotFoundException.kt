package com.findadoc.api.web

class DoctorNotFoundException(val slug: String) : RuntimeException("Doctor not found: $slug")
