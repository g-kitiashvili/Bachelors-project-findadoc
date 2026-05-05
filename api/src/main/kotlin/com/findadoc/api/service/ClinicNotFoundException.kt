package com.findadoc.api.service

class ClinicNotFoundException(val slug: String) : RuntimeException("Clinic not found: $slug")
