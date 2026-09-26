package com.example.marine.data.model

import com.google.gson.annotations.SerializedName

data class AskRequest(
    val question: String
)

data class AskResponse(
    val question: String? = null,
    val analysis: AskAnalysis? = null,
    @SerializedName("root_causes")
    val rootCauses: List<String> = emptyList(),
    val report: String? = null,
)

data class AskAnalysis(
    @SerializedName("avg_carbon_emission")
    val avgCarbonEmission: Double? = null,
    @SerializedName("avg_fuel_consumption")
    val avgFuelConsumption: Double? = null,
    @SerializedName("avg_engine_load")
    val avgEngineLoad: Double? = null,
    @SerializedName("avg_speed")
    val avgSpeed: Double? = null,
    @SerializedName("avg_wave_height")
    val avgWaveHeight: Double? = null,
    @SerializedName("avg_wind_speed")
    val avgWindSpeed: Double? = null,
)