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
data class DoctorClinicId(
    @Column(name = "doctor_id") val doctorId: Long = 0,
    @Column(name = "clinic_id") val clinicId: Long = 0,
) : Serializable

@Entity
@Table(name = "doctor_clinic")
class DoctorClinic(
    @EmbeddedId val id: DoctorClinicId,
    @ManyToOne @MapsId("doctorId") @JoinColumn(name = "doctor_id") val doctor: Doctor,
    @ManyToOne @MapsId("clinicId") @JoinColumn(name = "clinic_id") val clinic: Clinic,
)
