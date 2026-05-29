package com.findadoc.api.web

import com.findadoc.api.search.SearchResolver
import com.findadoc.api.search.SearchTargetType
import com.findadoc.api.web.dto.SearchResolutionDto
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/search")
@Tag(name = "Search", description = "Resolves a free-text query to the best doctor-search target.")
class SearchController(
    private val searchResolver: SearchResolver,
) {
    @Operation(summary = "Resolve a query to its best target (specialty, condition, or raw query)")
    @GetMapping("/resolve")
    fun resolve(@RequestParam(required = false) q: String?): SearchResolutionDto {
        val term = q?.trim()
        if (term.isNullOrEmpty()) return SearchResolutionDto("query", null, "")
        val best = searchResolver.resolve(term.lowercase())
            ?: return SearchResolutionDto("query", null, term)
        return SearchResolutionDto(
            type = when (best.type) {
                SearchTargetType.SPECIALTY -> "specialty"
                SearchTargetType.CONDITION -> "condition"
            },
            slug = best.slug,
            label = best.nameEn,
        )
    }
}
