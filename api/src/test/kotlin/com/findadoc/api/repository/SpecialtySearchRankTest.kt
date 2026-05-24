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
class SpecialtySearchRankTest @Autowired constructor(
    private val specialtyRepository: SpecialtyRepository,
) {
    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank resolves an english alias to its specialty with an exact flag and count`() {
        val hits = specialtyRepository.searchRank("heart", 0.30, 5)
        val cardio = hits.first { it.slug == "cardiology" }
        assertEquals(SearchTargetType.SPECIALTY, cardio.type)
        assertTrue(cardio.exact)
        assertEquals(2, cardio.doctorCount)
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank resolves a georgian alias`() {
        val hits = specialtyRepository.searchRank("კანი", 0.30, 5)
        assertTrue(hits.any { it.slug == "dermatology" })
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank matches the specialty name fuzzily`() {
        val hits = specialtyRepository.searchRank("cardio", 0.30, 5)
        assertTrue(hits.any { it.slug == "cardiology" })
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank matches a singular query against a plural alias`() {
        // alias is 'eyes'; the singular 'eye' must still resolve to ophthalmology
        val hits = specialtyRepository.searchRank("eye", 0.30, 5)
        val ophthalmology = hits.first { it.slug == "ophthalmology" }
        assertTrue(ophthalmology.exact)
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `searchRank returns nothing below threshold`() {
        assertTrue(specialtyRepository.searchRank("zzzzqqqq", 0.30, 5).isEmpty())
    }
}
