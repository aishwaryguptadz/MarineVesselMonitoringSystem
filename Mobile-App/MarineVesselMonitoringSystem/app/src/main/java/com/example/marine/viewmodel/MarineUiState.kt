package com.example.marine.viewmodel

import com.example.marine.data.model.AskAnalysis
import com.example.marine.data.model.Route

data class MarineUiState(
    val origin: String = "",
    val destination: String = "",
    val shipType: String = "",

    val routes: List<Route> = emptyList(),
    val selectedRoute: Route? = null,

    val isLoadingRoutes: Boolean = false,
    val routeError: String? = null,

    val healthScore: Double? = null,
    val alertLevel: String? = null,
    val isLoadingHealth: Boolean = false,
    val healthError: String? = null,

    val remainingLifeHours: Double? = null,
    val isLoadingLifetime: Boolean = false,
    val lifetimeError: String? = null,

    val assistantAnalysis: AskAnalysis? = null,
    val assistantReport: String? = null,
    val rootCauses: List<String> = emptyList(),
    val isLoadingAssistant: Boolean = false,
    val assistantError: String? = null,

    val isTestingConnection: Boolean = false,
    val connectionStatus: String? = null,
    val connectionError: String? = null
)