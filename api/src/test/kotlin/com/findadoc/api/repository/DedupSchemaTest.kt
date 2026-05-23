package com.findadoc.api.repository

import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.transaction.annotation.Transactional
import kotlin.test.assertEquals

@SpringBootTest
@Transactional
class DedupSchemaTest @Autowired constructor(
    private val dsl: DSLContext,
) {
    @Test
    fun `merged status is allowed and merge columns exist`() {
        dsl.execute(
            "INSERT INTO doctor (slug, full_name_ka, full_name_en, last_source_url, last_updated_at, status, merged_into_id) " +
                "VALUES ('dedup-schema-probe','პ','P','https://example.test/probe', now(), 'MERGED', NULL)",
        )
        assertEquals(1, dsl.fetchCount(DSL.table("doctor"), DSL.field("slug").eq("dedup-schema-probe")))
        dsl.execute("SELECT via_merge FROM doctor_clinic LIMIT 0")
        dsl.execute("SELECT via_merge FROM doctor_specialty LIMIT 0")
    }
}
