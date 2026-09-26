package com.example.marine.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marine.data.model.Route
import com.example.marine.data.remote.RetrofitClient
import com.example.marine.data.repository.MarineRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.collections.copy

class MarineViewModel : ViewModel() {

    private val repository = MarineRepository(
        RetrofitClient.api
    )

    private val _uiState = MutableStateFlow(MarineUiState())

    val uiState: StateFlow<MarineUiState> =
        _uiState.asStateFlow()

    fun testConnection() {
        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    isTestingConnection = true,
                    connectionStatus = null,
                    connectionError = null
                )
            }

            repository.testConnection()
                .onSuccess {
                    _uiState.update { state ->
                        state.copy(
                            isTestingConnection = false,
                            connectionStatus = "Backend connection successful",
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update { state ->
                        state.copy(
                            isTestingConnection = false,
                            connectionError = "${error.javaClass.simpleName}: ${error.message}"
                        )
                    }
                }
        }
    }

    fun getRoutes(
        origin: String,
        destination: String,
        shipType: String? = null
    ) {
        viewModelScope.launch {

            _uiState.value = _uiState.value.copy(
                isLoadingRoutes = true,
                routeError = null
            )

            repository.getRoutes(
                origin = origin,
                destination = destination,
                shipType = shipType
            ).onSuccess { response ->
                _uiState.update {
                    it.copy(
                        isLoadingRoutes = false,
                        routes = response.routes,
                        selectedRoute = response.routes.firstOrNull(),
                        routeError = null
                    )
                }
            }
        }
    }

    fun predictHealth(
        rpm: Double,
        engineTemp: Double,
        vibration: Double,
        loadWeight: Double
    ) {
        viewModelScope.launch {

            _uiState.update {
                it.copy(
                    isLoadingHealth = true,
                    healthError = null,
                    healthScore = null,
                    alertLevel = null
                )
            }

            repository.predictHealth(
                rpm = rpm,
                engineTemp = engineTemp,
                vibration = vibration,
                loadWeight = loadWeight
            )
                .onSuccess { response ->

                    _uiState.update {
                        it.copy(
                            isLoadingHealth = false,
                            healthScore = response.healthScore,
                            alertLevel = response.alertLevel,
                            healthError = null
                        )
                    }
                }
                .onFailure { error ->

                    _uiState.update {
                        it.copy(
                            isLoadingHealth = false,
                            healthError = error.message ?: "Unknown error"
                        )
                    }
                }
        }
    }

    fun getVoyageHealth(
        origin: String,
        destination: String,
        shipType: String?,
        routeIndex: Int
    ) {
        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    isLoadingHealth = true,
                    healthError = null
                )
            }

            repository
                .getVoyageHealth(
                    origin = origin,
                    destination = destination,
                    shipType = shipType,
                    routeIndex = routeIndex
                )
                .onSuccess { response ->
                    _uiState.update {
                        it.copy(
                            isLoadingHealth = false,
                            selectedRoute = response.selectedRoute,
                            healthScore = response.healthScore,
                            alertLevel = response.alertLevel,
                            healthError = response.error
                        )
                    }
                }
        }
    }

    fun predictLifetime(
        rpm: Double,
        engineTemp: Double,
        vibration: Double,
        loadWeight: Double
    ) {
        viewModelScope.launch {

            _uiState.value = _uiState.value.copy(
                isLoadingLifetime = true,
                lifetimeError = null
            )

            repository.predictLifetime(
                rpm = rpm,
                engineTemp = engineTemp,
                vibration = vibration,
                loadWeight = loadWeight
            ).onSuccess { response ->

                if (response.error != null) {
                    _uiState.value = _uiState.value.copy(
                        isLoadingLifetime = false,
                        lifetimeError = response.error
                    )
                    return@onSuccess
                }

                _uiState.value = _uiState.value.copy(
                    remainingLifeHours = response.remainingLifeHours,
                    isLoadingLifetime = false,
                    lifetimeError = null
                )

            }.onFailure { exception ->

                _uiState.value = _uiState.value.copy(
                    isLoadingLifetime = false,
                    lifetimeError = exception.message
                        ?: "Unable to predict lifetime"
                )
            }
        }
    }

    fun askAssistant(question: String) {
        if (question.isBlank()) return

        viewModelScope.launch {

            _uiState.update {
                it.copy(
                    isLoadingAssistant = true,
                    assistantError = null
                )
            }

            repository.askAssistant(question)
                .onSuccess { response ->
                    _uiState.update {
                        it.copy(
                            isLoadingAssistant = false,
                            assistantAnalysis = response.analysis,
                            assistantReport = response.report,
                            rootCauses = response.rootCauses,
                            assistantError = null
                        )
                    }
                }

                .onFailure { error ->

                    _uiState.update {
                        it.copy(
                            isLoadingAssistant = false,
                            assistantError =
                                error.message ?: "Unable to get AI response."
                        )
                    }
                }
        }
    }

    fun analyzeVoyage(
        origin: String,
        destination: String,
        shipType: String
    ) {
        viewModelScope.launch {

            _uiState.update {
                it.copy(
                    origin = origin,
                    destination = destination,
                    shipType = shipType,

                    isLoadingRoutes = true,
                    isLoadingHealth = true,

                    routeError = null,
                    healthError = null
                )
            }

            // Get all route recommendations
            repository
                .getRoutes(
                    origin = origin,
                    destination = destination,
                    shipType = shipType
                )
                .onSuccess { response ->

                    _uiState.update {
                        it.copy(
                            isLoadingRoutes = false,
                            routes = response.routes,
                            selectedRoute = response.routes.firstOrNull(),
                            routeError = null
                        )
                    }
                }
                .onFailure { error ->

                    _uiState.update {
                        it.copy(
                            isLoadingRoutes = false,
                            routeError =
                                error.message ?: "Failed to load routes"
                        )
                    }
                }

            // Get health + selected route
            repository
                .getVoyageHealth(
                    origin = origin,
                    destination = destination,
                    shipType = shipType,
                    routeIndex = 0
                )
                .onSuccess { response ->

                    _uiState.update {
                        it.copy(
                            isLoadingHealth = false,
                            selectedRoute = response.selectedRoute,
                            healthScore = response.healthScore,
                            alertLevel = response.alertLevel,
                            healthError = response.error
                        )
                    }
                }
                .onFailure { error ->

                    _uiState.update {
                        it.copy(
                            isLoadingHealth = false,
                            healthError =
                                error.message ?: "Failed to analyze vessel health"
                        )
                    }
                }
        }
    }

    fun selectRoute(route: Route) {
        _uiState.update {
            it.copy(
                selectedRoute = route
            )
        }
    }


    fun resetVoyage() {
        _uiState.update {
            it.copy(
                origin = "",
                destination = "",
                shipType = "",

                routes = emptyList(),
                selectedRoute = null,

                healthScore = null,
                alertLevel = null,

                remainingLifeHours = null,

                routeError = null,
                healthError = null,
                lifetimeError = null,

                assistantAnalysis = null,
                assistantReport = null,
                rootCauses = emptyList(),
                assistantError = null
            )
        }
    }
}