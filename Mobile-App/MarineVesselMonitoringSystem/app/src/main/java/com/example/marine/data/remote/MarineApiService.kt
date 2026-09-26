package com.example.marine.data.remote

import com.example.marine.data.model.AskRequest
import com.example.marine.data.model.AskResponse
import com.example.marine.data.model.HealthRequest
import com.example.marine.data.model.HealthResponse
import com.example.marine.data.model.LifetimeResponse
import com.example.marine.data.model.RouteRequest
import com.example.marine.data.model.RouteResponse
import com.example.marine.data.model.VoyageHealthRequest
import com.example.marine.data.model.VoyageHealthResponse
import okhttp3.ResponseBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface MarineApiService {

    @GET("docs")
    suspend fun testConnection(): ResponseBody

    @POST("route")
    suspend fun getRoutes(
        @Body request: RouteRequest
    ): RouteResponse

    @POST("prediction/health")
    suspend fun predictHealth(
        @Body request: HealthRequest
    ): HealthResponse

    @POST("voyage/health")
    suspend fun getVoyageHealth(
        @Body request: VoyageHealthRequest
    ): VoyageHealthResponse

    @POST("prediction/lifetime")
    suspend fun predictLifetime(
        @Body request: HealthRequest
    ): LifetimeResponse

    @POST("ask")
    suspend fun askAssistant(
        @Body request: AskRequest
    ): AskResponse

}