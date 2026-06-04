package com.findadoc.api.exception

class SpecialtyNotFoundException(val slug: String) : RuntimeException("Specialty not found: $slug")
