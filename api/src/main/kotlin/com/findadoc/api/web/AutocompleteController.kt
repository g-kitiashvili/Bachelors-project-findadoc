package com.findadoc.api.web

import com.findadoc.api.service.AutocompleteService
import com.findadoc.api.web.dto.AutocompleteResponseDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/autocomplete")
@Tag(name = "Autocomplete", description = "Grouped doctor and specialty suggestions for the search bar.")
class AutocompleteController(
    private val autocompleteService: AutocompleteService,
) {
    @Operation(summary = "Grouped suggestions for a search term")
    @GetMapping
    fun getSuggestions(@RequestParam(required = false) q: String?): AutocompleteResponseDto =
        autocompleteService.suggest(q)
}
