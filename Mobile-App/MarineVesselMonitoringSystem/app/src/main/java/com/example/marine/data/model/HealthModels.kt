package com.example.marine.data.model

import com.google.gson.annotations.SerializedName

data class HealthRequest(
    val rpm: Double,
    val engineTemp: Double,
    val vibration: Double,
    val loadWeight: Double
)

data class HealthResponse(

    @SerializedName("health_score")
    val healthScore: Double? = null,
    @SerializedName("alert_level")
    val alertLevel: String? = null,
    val error: String? = null
)