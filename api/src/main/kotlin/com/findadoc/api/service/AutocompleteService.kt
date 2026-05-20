package com.findadoc.api.service

import com.findadoc.api.repository.ClinicRepository
import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.repository.jooq.FUZZY_THRESHOLD
import com.findadoc.api.search.SearchResolver
import com.findadoc.api.search.SearchTargetType
import com.findadoc.api.web.dto.AutocompleteResponseDto
import com.findadoc.api.web.dto.ConditionSuggestionDto
import com.findadoc.api.web.dto.SpecialtySuggestionDto
import com.findadoc.api.web.dto.toSuggestionDto
import org.springframework.data.domain.PageRequest
import org.springframework.stereotype.Service

@Service
class AutocompleteService(
    private val doctorRepository: DoctorRepository,
    private val clinicRepository: ClinicRepository,
    private val searchResolver: SearchResolver,
) {
    fun suggest(q: String?): AutocompleteResponseDto {
        val term = q?.trim()
        if (term == null || term.length < MIN_QUERY_LENGTH) {
            return AutocompleteResponseDto(emptyList(), emptyList(), emptyList(), emptyList())
        }
        val lower = term.lowercase()

        val doctors = doctorRepository.findFiltered(
            filter = DoctorFilter(q = lower),
            sort = "relevancy",
            pageable = PageRequest.of(0, GROUP_CAP),
        ).content.map { it.toSuggestionDto() }

        val ranked = searchResolver.rank(lower, GROUP_CAP)
        val specialties = ranked.filter { it.type == SearchTargetType.SPECIALTY }
            .map { SpecialtySuggestionDto(it.slug, it.nameEn, it.nameKa, it.doctorCount) }
        val conditions = ranked.filter { it.type == SearchTargetType.CONDITION }
            .map { ConditionSuggestionDto(it.slug, it.nameEn, it.nameKa, it.doctorCount) }

        val clinics = clinicRepository.autocomplete(lower, FUZZY_THRESHOLD, GROUP_CAP)

        return AutocompleteResponseDto(doctors, specialties, conditions, clinics)
    }

    private companion object {
        const val MIN_QUERY_LENGTH = 2
        const val GROUP_CAP = 5
    }
}
