package com.findadoc.api.repository

import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import kotlin.test.assertEquals

@SpringBootTest
class JooqSmokeTest @Autowired constructor(
    private val dsl: DSLContext,
) {
    @Test
    fun `dsl context executes a trivial query`() {
        val one = dsl.select(DSL.inline(1)).fetchOne(0, Int::class.java)
        assertEquals(1, one)
    }
}
