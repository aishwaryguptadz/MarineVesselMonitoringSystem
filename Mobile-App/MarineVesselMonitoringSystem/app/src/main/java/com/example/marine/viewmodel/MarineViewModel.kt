package com.example.marine.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marine.data.remote.RetrofitClient
import com.example.marine.data.repository.MarineRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

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
        viewModelScope.launch {

            _uiState.value = _uiState.value.copy(
                isLoadingAssistant = true,
                assistantError = null
            )

            repository.askAssistant(question)
                .onSuccess { response ->

                    _uiState.value = _uiState.value.copy(
                        assistantAnswer = response.report,
                        rootCauses = response.rootCauses,
                        isLoadingAssistant = false,
                        assistantError = null
                    )

                }.onFailure { exception ->

                    _uiState.value = _uiState.value.copy(
                        isLoadingAssistant = false,
                        assistantError = exception.message
                            ?: "Unable to contact AI assistant"
                    )
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
}