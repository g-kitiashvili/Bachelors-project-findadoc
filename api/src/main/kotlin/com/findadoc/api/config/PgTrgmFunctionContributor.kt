package com.findadoc.api.config

import org.hibernate.boot.model.FunctionContributions
import org.hibernate.boot.model.FunctionContributor
import org.hibernate.type.StandardBasicTypes

class PgTrgmFunctionContributor : FunctionContributor {
    override fun contributeFunctions(contributions: FunctionContributions) {
        val registry = contributions.functionRegistry
        val doubleType = contributions.typeConfiguration.basicTypeRegistry.resolve(StandardBasicTypes.DOUBLE)
        registry.registerPattern("word_similarity", "word_similarity(?1, ?2)", doubleType)
    }
}
