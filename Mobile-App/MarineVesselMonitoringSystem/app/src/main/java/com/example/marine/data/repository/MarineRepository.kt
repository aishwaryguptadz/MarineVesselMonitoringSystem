package com.example.marine.data.repository

import com.example.marine.data.model.AskRequest
import com.example.marine.data.model.AskResponse
import com.example.marine.data.model.HealthRequest
import com.example.marine.data.model.HealthResponse
import com.example.marine.data.model.LifetimeResponse
import com.example.marine.data.model.RouteRequest
import com.example.marine.data.model.RouteResponse
import com.example.marine.data.model.VoyageHealthRequest
import com.example.marine.data.model.VoyageHealthResponse
import com.example.marine.data.remote.MarineApiService

class MarineRepository(private val api: MarineApiService) {

    suspend fun testConnection(): Result<String> =
        runCatching { api.testConnection().string() }

    suspend fun getRoutes(
        origin: String,
        destination: String,
        shipType: String?
    ): Result<RouteResponse> {
        return runCatching {
            api.getRoutes(
                RouteRequest(
                    origin = origin,
                    destination = destination,
                    shipType = shipType
                )
            )
        }
    }

    suspend fun predictHealth(
        rpm: Double,
        engineTemp: Double,
        vibration: Double,
        loadWeight: Double
    ): Result<HealthResponse> =
        runCatching {
            api.predictHealth(
                HealthRequest(
                    rpm = rpm,
                    engineTemp = engineTemp,
                    vibration = vibration,
                    loadWeight = loadWeight
                )
            )
        }

    suspend fun getVoyageHealth(
        origin: String,
        destination: String,
        shipType: String?,
        routeIndex: Int
    ): Result<VoyageHealthResponse> {
        return runCatching {
            api.getVoyageHealth(
                VoyageHealthRequest(
                    origin = origin,
                    destination = destination,
                    shipType = shipType,
                    routeIndex = routeIndex
                )
            )
        }
    }

    suspend fun predictLifetime(
        rpm: Double,
        engineTemp: Double,
        vibration: Double,
        loadWeight: Double
    ): Result<LifetimeResponse> {
        return runCatching {
            api.predictLifetime(
                HealthRequest(
                    rpm = rpm,
                    engineTemp = engineTemp,
                    vibration = vibration,
                    loadWeight = loadWeight
                )
            )
        }
    }

    suspend fun askAssistant(
        question: String
    ): Result<AskResponse> {
        return runCatching {
            api.askAssistant(
                AskRequest(question)
            )
        }
    }
}