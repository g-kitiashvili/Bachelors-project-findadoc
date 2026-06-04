package com.findadoc.api.exception

class DoctorNotFoundException(val slug: String) : RuntimeException("Doctor not found: $slug")
