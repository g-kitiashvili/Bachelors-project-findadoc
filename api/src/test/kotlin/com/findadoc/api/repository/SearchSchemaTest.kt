package com.findadoc.api.repository

import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.jdbc.Sql
import org.springframework.transaction.annotation.Transactional
import kotlin.test.assertEquals

@SpringBootTest
@Transactional
class SearchSchemaTest @Autowired constructor(
    private val dsl: DSLContext,
) {
    @Test
    @Sql("/sql/search-test-fixture.sql")
    fun `search term tables accept seeded rows`() {
        assertEquals(3, dsl.fetchCount(DSL.table("specialty_alias")))
        assertEquals(2, dsl.fetchCount(DSL.table("condition_synonym")))
    }
}
