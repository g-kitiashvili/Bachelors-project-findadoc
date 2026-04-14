package com.findadoc.api.web

import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.test.context.jdbc.Sql
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get
import org.springframework.transaction.annotation.Transactional

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class DoctorListTest @Autowired constructor(
    private val mockMvc: MockMvc,
) {
    @Test
    @Sql(value = ["/sql/cleanup.sql"], executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
    fun `getAll returns empty page when no doctors`() {
        mockMvc.get("/api/v1/doctors")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(0) }
                jsonPath("$.total") { value(0) }
                jsonPath("$.page") { value(1) }
                jsonPath("$.pageSize") { value(5) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll returns first page with default pageSize 5`() {
        mockMvc.get("/api/v1/doctors")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(5) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(1) }
                jsonPath("$.pageSize") { value(5) }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
                jsonPath("$.items[4].slug") { value("nika-kapanadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll page=2 returns remaining 2 doctors`() {
        mockMvc.get("/api/v1/doctors?page=2")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(2) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(2) }
                jsonPath("$.items[0].slug") { value("tamar-maisuradze") }
                jsonPath("$.items[1].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll page=999 returns empty items with correct total`() {
        mockMvc.get("/api/v1/doctors?page=999")
            .andExpect {
                status { isOk() }
                jsonPath("$.items.length()") { value(0) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.page") { value(999) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll pageSize over max clamps to 50`() {
        mockMvc.get("/api/v1/doctors?pageSize=1000")
            .andExpect {
                status { isOk() }
                jsonPath("$.pageSize") { value(50) }
                jsonPath("$.items.length()") { value(7) }
                jsonPath("$.total") { value(7) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll excludes INACTIVE doctors`() {
        mockMvc.get("/api/v1/doctors?pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[?(@.slug == 'inactive-test')]") { isEmpty() }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches en typo`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Giorggi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches ka substring`() {
        mockMvc.get("/api/v1/doctors") { param("q", "ცინცა") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches en specialty substring`() {
        mockMvc.get("/api/v1/doctors") { param("q", "kardio") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches ka specialty substring`() {
        mockMvc.get("/api/v1/doctors") { param("q", "კარდი") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches ka name typo with missing letter`() {
        mockMvc.get("/api/v1/doctors") { param("q", "მარიმ") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches transposed letter typo`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Marima") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q fuzzy matches surname substring`() {
        mockMvc.get("/api/v1/doctors") { param("q", "javakhi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("luka-javakhishvili") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q ranks exact match first`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Giorgi") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q below threshold returns empty`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Xenobiology") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q excludes inactive doctors`() {
        mockMvc.get("/api/v1/doctors") { param("q", "Inactive") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with specialty filter narrows to that specialty only`() {
        mockMvc.get("/api/v1/doctors") { param("specialty", "cardiology") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(2) }
                jsonPath("$.items[0].primarySpecialty.slug") { value("cardiology") }
                jsonPath("$.items[1].primarySpecialty.slug") { value("cardiology") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with multiple specialty slugs returns union`() {
        mockMvc.get("/api/v1/doctors") { param("specialty", "cardiology,pediatrics") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(3) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with q and specialty returns intersection`() {
        mockMvc.get("/api/v1/doctors") {
            param("q", "giorgi")
            param("specialty", "cardiology")
        }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll with unknown specialty slug returns no doctors`() {
        mockMvc.get("/api/v1/doctors") { param("specialty", "does-not-exist") }
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(0) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll items include primarySpecialty when mapped`() {
        mockMvc.get("/api/v1/doctors") { param("specialty", "cardiology") }
            .andExpect {
                status { isOk() }
                jsonPath("$.items[0].primarySpecialty.nameEn") { value("Cardiology") }
                jsonPath("$.items[0].primarySpecialty.nameKa") { value("კარდიოლოგია") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll region filter returns only doctors in that region`() {
        mockMvc.get("/api/v1/doctors?region=imereti")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("doc-kutaisi") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll region filter matches region-level attribution`() {
        mockMvc.get("/api/v1/doctors?region=tbilisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("doc-tbilisi") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll city filter returns only doctors in that city`() {
        mockMvc.get("/api/v1/doctors?city=kutaisi")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("doc-kutaisi") }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll region and specialty filters combine with AND`() {
        mockMvc.get("/api/v1/doctors?region=imereti&specialty=cardiology")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(1) }
                jsonPath("$.items[0].slug") { value("doc-kutaisi") }
            }
        mockMvc.get("/api/v1/doctors?region=tbilisi&specialty=cardiology")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(0) }
            }
    }

    @Test
    @Sql("/sql/locations-test-fixture.sql")
    fun `getAll without location filter includes doctors with no location`() {
        mockMvc.get("/api/v1/doctors?pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(3) }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll sort=atoz returns doctors alphabetically by name`() {
        mockMvc.get("/api/v1/doctors?sort=atoz&pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
                jsonPath("$.items[1].slug") { value("ana-eradze") }
                jsonPath("$.items[6].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll sort=ztoa returns doctors reverse alphabetically by name`() {
        mockMvc.get("/api/v1/doctors?sort=ztoa&pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
                jsonPath("$.items[1].slug") { value("tamar-maisuradze") }
                jsonPath("$.items[6].slug") { value("mariam-beridze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll sort=relevancy with query ranks best match first`() {
        mockMvc.get("/api/v1/doctors") {
            param("q", "Giorgi")
            param("sort", "relevancy")
        }.andExpect {
            status { isOk() }
            jsonPath("$.items[0].slug") { value("giorgi-tsintsadze") }
        }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll sort=relevancy without query falls back to alphabetical`() {
        mockMvc.get("/api/v1/doctors?sort=relevancy&pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
                jsonPath("$.items[6].slug") { value("giorgi-tsintsadze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll sort=atoz with query overrides relevancy ordering`() {
        mockMvc.get("/api/v1/doctors") {
            param("q", "shvili")
            param("sort", "atoz")
        }.andExpect {
            status { isOk() }
            jsonPath("$.total") { value(2) }
            jsonPath("$.items[0].slug") { value("davit-gelashvili") }
            jsonPath("$.items[1].slug") { value("luka-javakhishvili") }
        }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll unknown sort value falls back to default order`() {
        mockMvc.get("/api/v1/doctors?sort=bogus&pageSize=50")
            .andExpect {
                status { isOk() }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items[0].slug") { value("mariam-beridze") }
            }
    }

    @Test
    @Sql("/sql/doctors-test-fixture.sql")
    fun `getAll page=0 coerces to first page`() {
        mockMvc.get("/api/v1/doctors?page=0")
            .andExpect {
                status { isOk() }
                jsonPath("$.page") { value(1) }
                jsonPath("$.total") { value(7) }
                jsonPath("$.items.length()") { value(5) }
            }
    }
}
