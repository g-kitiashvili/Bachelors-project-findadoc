package com.findadoc.api.search

import com.findadoc.api.repository.MedicalConditionRepository
import com.findadoc.api.repository.SpecialtyRepository
import org.springframework.stereotype.Service

const val SPECIALTY_SUGGEST_THRESHOLD = 0.30
const val CONDITION_SUGGEST_THRESHOLD = 0.65
const val RESOLVE_THRESHOLD = 0.50

@Service
class SearchResolver(
    private val specialtyRepository: SpecialtyRepository,
    private val medicalConditionRepository: MedicalConditionRepository,
) {
    fun rank(q: String, limitPerType: Int): List<RankedTarget> {
        val specialties = specialtyRepository.searchRank(q, SPECIALTY_SUGGEST_THRESHOLD, limitPerType)
        val conditions = medicalConditionRepository.searchRank(q, CONDITION_SUGGEST_THRESHOLD, limitPerType)
        return (specialties + conditions).sortedWith(
            compareByDescending<RankedTarget> { it.exact }
                .thenByDescending { it.score }
                .thenByDescending { it.doctorCount }
                .thenBy { it.type }
                .thenBy { it.slug },
        )
    }

    fun resolve(q: String): RankedTarget? =
        rank(q, RESOLVE_LIMIT).firstOrNull()?.takeIf { it.exact || it.score >= RESOLVE_THRESHOLD }

    private companion object {
        const val RESOLVE_LIMIT = 5
    }
}
