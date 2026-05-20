package com.findadoc.api.search

import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.jdbc.Sql
import org.springframework.transaction.annotation.Transactional
import kotlin.test.assertEquals
import kotlin.test.assertNull

@SpringBootTest
@Transactional
class SearchResolverTest @Autowired constructor(
    private val searchResolver: SearchResolver,
) {
    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve routes a lay body-part term to its specialty`() {
        val best = searchResolver.resolve("heart")
        assertEquals(SearchTargetType.SPECIALTY, best?.type)
        assertEquals("cardiology", best?.slug)
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve routes a condition synonym to its condition`() {
        val best = searchResolver.resolve("high blood pressure")
        assertEquals(SearchTargetType.CONDITION, best?.type)
        assertEquals("hypertension", best?.slug)
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `resolve returns null when nothing clears the bar`() {
        assertNull(searchResolver.resolve("zzzzqqqq"))
    }

    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `rank exposes both target types for a shared term`() {
        val ranked = searchResolver.rank("cardiology", 5)
        assertEquals("cardiology", ranked.first().slug)
    }
}
