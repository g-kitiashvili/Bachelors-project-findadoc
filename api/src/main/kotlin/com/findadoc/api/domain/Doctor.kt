package com.findadoc.api.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import java.time.OffsetDateTime

@Entity
@Table(name = "doctor")
class Doctor(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false, unique = true)
    val slug: String,

    @Column(name = "full_name_ka", nullable = false)
    val fullNameKa: String,

    @Column(name = "full_name_en", nullable = false)
    val fullNameEn: String,

    @Column(name = "family_name_ka")
    val familyNameKa: String? = null,

    @Column(name = "family_name_en")
    val familyNameEn: String? = null,

    @Column(name = "gender")
    val gender: String? = null,

    @Column(name = "photo_url")
    val photoUrl: String? = null,

    @Column(name = "specialty_ka")
    val specialtyKa: String? = null,

    @Column(name = "specialty_en")
    val specialtyEn: String? = null,

    @Column(name = "is_accepting_new_patients", nullable = false)
    val isAcceptingNewPatients: Boolean = true,

    @Column(name = "treats_children", nullable = false)
    val treatsChildren: Boolean = false,

    @Column(name = "treats_adults", nullable = false)
    val treatsAdults: Boolean = true,

    @Column(name = "bio_ka")
    val bioKa: String? = null,

    @Column(name = "bio_en")
    val bioEn: String? = null,

    @Column(name = "last_source_url")
    val lastSourceUrl: String? = null,

    @Column(name = "last_updated_at")
    val lastUpdatedAt: OffsetDateTime? = null,

    @Column(name = "status", nullable = false)
    val status: String = "ACTIVE",

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: OffsetDateTime = OffsetDateTime.now(),

    @OneToMany(mappedBy = "doctor")
    val doctorSpecialties: List<DoctorSpecialty> = emptyList(),

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "location_id")
    val location: Location? = null,
)
