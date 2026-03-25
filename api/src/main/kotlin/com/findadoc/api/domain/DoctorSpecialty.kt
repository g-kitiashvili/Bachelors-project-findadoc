package com.findadoc.api.domain

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.MapsId
import jakarta.persistence.Table
import java.io.Serializable

@Embeddable
data class DoctorSpecialtyId(
    @Column(name = "doctor_id") val doctorId: Long = 0,
    @Column(name = "specialty_id") val specialtyId: Long = 0,
) : Serializable

@Entity
@Table(name = "doctor_specialty")
class DoctorSpecialty(
    @EmbeddedId
    val id: DoctorSpecialtyId,

    @ManyToOne
    @MapsId("doctorId")
    @JoinColumn(name = "doctor_id")
    val doctor: Doctor,

    @ManyToOne
    @MapsId("specialtyId")
    @JoinColumn(name = "specialty_id")
    val specialty: Specialty,

    @Column(name = "is_primary", nullable = false)
    val isPrimary: Boolean = false,
)
