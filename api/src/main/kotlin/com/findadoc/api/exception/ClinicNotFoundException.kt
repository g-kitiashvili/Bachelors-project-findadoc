package com.findadoc.api.exception

class ClinicNotFoundException(val slug: String) : RuntimeException("Clinic not found: $slug")
