package com.findadoc.api.service

class SpecialtyNotFoundException(val slug: String) : RuntimeException("Specialty not found: $slug")
