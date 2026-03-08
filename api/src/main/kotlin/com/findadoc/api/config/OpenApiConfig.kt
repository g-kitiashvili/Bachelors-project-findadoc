package com.findadoc.api.config

import io.swagger.v3.oas.models.OpenAPI
import io.swagger.v3.oas.models.info.Info
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class OpenApiConfig {

    @Bean
    fun openApi(): OpenAPI = OpenAPI().info(
        Info()
            .title("Find-a-Doc API")
            .description("Doctor and clinic search API for the Georgian healthcare market.")
            .version("0.1.0"),
    )
}
