package com.findadoc.api.repository

import com.findadoc.api.search.SearchTargetType
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.jdbc.Sql
import org.springframework.transaction.annotation.Transactional
import kotlin.test.assertEquals
import kotlin.test.assertTrue

@SpringBootTest
@Transactional
class MedicalConditionSearchRankTest @Autowired constructor(
    private val medicalConditionRepository: MedicalConditionRepository,
) {
    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank resolves an english synonym to its condition with count`() {
        val hits = medicalConditionRepository.searchRank("high blood pressure", 0.30, 5)
        val htn = hits.first { it.slug == "hypertension" }
        assertEquals(SearchTargetType.CONDITION, htn.type)
        assertTrue(htn.exact)
        assertEquals(2, htn.doctorCount)
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank resolves a georgian synonym`() {
        val hits = medicalConditionRepository.searchRank("მაღალი წნევა", 0.30, 5)
        assertTrue(hits.any { it.slug == "hypertension" })
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank returns nothing below threshold`() {
        assertTrue(medicalConditionRepository.searchRank("zzzzqqqq", 0.30, 5).isEmpty())
    }
}
