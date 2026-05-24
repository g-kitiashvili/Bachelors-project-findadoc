package com.findadoc.api.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.time.OffsetDateTime

@Entity
@Table(name = "clinic")
class Clinic(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    @Column(nullable = false, unique = true) val slug: String,
    @Column(name = "name_ka", nullable = false) val nameKa: String,
    @Column(name = "name_en", nullable = false) val nameEn: String,
    @Column(name = "address") val address: String? = null,
    @Column(name = "address_en") val addressEn: String? = null,
    @Column(name = "phone") val phone: String? = null,
    @Column(name = "website") val website: String? = null,
    @Column(name = "status", nullable = false) val status: String = "ACTIVE",
    @Column(name = "last_source_url", nullable = false, unique = true) val lastSourceUrl: String,
    @Column(name = "last_updated_at") val lastUpdatedAt: OffsetDateTime? = null,
    @Column(name = "created_at", nullable = false, updatable = false) val createdAt: OffsetDateTime = OffsetDateTime.now(),
)
