package com.example.marine.data.model

import com.google.gson.annotations.SerializedName

data class VoyageHealthRequest(
    val origin: String,
    val destination: String,
    val shipType: String? = null,
    val routeIndex: Int = 0
)

data class VoyageHealthResponse(
    @SerializedName("selected_route")
    val selectedRoute: Route? = null,
    @SerializedName("health_score")
    val healthScore: Double? = null,
    @SerializedName("alert_level")
    val alertLevel: String? = null,
    val error: String? = null
)