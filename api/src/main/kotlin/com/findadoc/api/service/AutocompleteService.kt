package com.findadoc.api.service

import com.findadoc.api.repository.ClinicRepository
import com.findadoc.api.repository.DoctorRepository
import com.findadoc.api.repository.SpecialtyRepository
import com.findadoc.api.repository.jooq.DoctorFilter
import com.findadoc.api.repository.jooq.FUZZY_THRESHOLD
import com.findadoc.api.web.dto.AutocompleteResponseDto
import com.findadoc.api.web.dto.toSuggestionDto
import org.springframework.data.domain.PageRequest
import org.springframework.stereotype.Service

@Service
class AutocompleteService(
    private val doctorRepository: DoctorRepository,
    private val specialtyRepository: SpecialtyRepository,
    private val clinicRepository: ClinicRepository,
) {
    fun suggest(q: String?): AutocompleteResponseDto {
        val term = q?.trim()
        if (term == null || term.length < MIN_QUERY_LENGTH) {
            return AutocompleteResponseDto(doctors = emptyList(), specialties = emptyList(), clinics = emptyList())
        }
        val lower = term.lowercase()
        val limit = PageRequest.of(0, GROUP_CAP)

        val doctors = doctorRepository.findFiltered(
            filter = DoctorFilter(q = lower),
            sort = "relevancy",
            pageable = limit,
        ).content.map { it.toSuggestionDto() }

        val specialties = specialtyRepository.autocomplete(lower, FUZZY_THRESHOLD, GROUP_CAP)

        val clinics = clinicRepository.autocomplete(lower, FUZZY_THRESHOLD, GROUP_CAP)

        return AutocompleteResponseDto(doctors = doctors, specialties = specialties, clinics = clinics)
    }

    companion object {
        private const val MIN_QUERY_LENGTH = 2
        private const val GROUP_CAP = 5
    }
}
