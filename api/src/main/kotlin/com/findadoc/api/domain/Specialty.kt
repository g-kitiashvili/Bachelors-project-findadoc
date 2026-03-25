package com.findadoc.api.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import java.time.OffsetDateTime

@Entity
@Table(name = "specialty")
class Specialty(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false, unique = true)
    val slug: String,

    @Column(name = "name_ka", nullable = false)
    val nameKa: String,

    @Column(name = "name_en", nullable = false)
    val nameEn: String,

    @Column(name = "description_ka")
    val descriptionKa: String? = null,

    @Column(name = "description_en")
    val descriptionEn: String? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    val parent: Specialty? = null,

    @Column(name = "sort_order", nullable = false)
    val sortOrder: Int = 1000,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: OffsetDateTime = OffsetDateTime.now(),
)
