package com.findadoc.api.repository

import com.findadoc.api.domain.Doctor
import org.springframework.data.jpa.domain.Specification

object DoctorSpecs {

    fun active(): Specification<Doctor> =
        Specification { root, _, cb -> cb.equal(root.get<String>("status"), "ACTIVE") }
}
