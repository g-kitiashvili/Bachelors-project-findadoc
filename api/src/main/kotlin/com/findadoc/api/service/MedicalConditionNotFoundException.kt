package com.findadoc.api.service

class MedicalConditionNotFoundException(val slug: String) : RuntimeException("Medical condition not found: $slug")
