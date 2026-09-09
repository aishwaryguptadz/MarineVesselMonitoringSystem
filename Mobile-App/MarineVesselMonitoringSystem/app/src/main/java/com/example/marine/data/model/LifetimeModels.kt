package com.example.marine.data.model

import com.google.gson.annotations.SerializedName

class LifetimeResponse(
    @SerializedName("remaining_life_hours")
    val remainingLifeHours: Double? = null,
    val error: String? = null
)