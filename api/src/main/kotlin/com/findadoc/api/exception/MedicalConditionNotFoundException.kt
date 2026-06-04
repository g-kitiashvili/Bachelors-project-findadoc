package com.findadoc.api.exception

class MedicalConditionNotFoundException(val slug: String) : RuntimeException("Medical condition not found: $slug")
