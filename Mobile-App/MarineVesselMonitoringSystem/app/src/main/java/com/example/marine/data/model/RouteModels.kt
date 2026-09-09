package com.example.marine.data.model

import com.google.gson.annotations.SerializedName

data class RouteRequest(
    val origin: String,
    val destination: String,
    val shipType: String? = null
)

data class RouteResponse(
    val routes: List<Route> = emptyList()
)

data class Route(
    val path: List<String> = emptyList(),
    @SerializedName("path_str")
    val pathStr: String = "",
    @SerializedName("n_legs")
    val nLegs: Int = 0,

    val legs: List<RouteLeg> = emptyList(),

    @SerializedName("total_fuel_t")
    val totalFuelT: Double = 0.0,
    @SerializedName("total_distance_nm")
    val totalDistanceNm: Double = 0.0,
    @SerializedName("total_voyage_days")
    val totalVoyageDays: Double = 0.0,
    @SerializedName("total_fuel_cost_usd")
    val totalFuelCostUsd: Double = 0.0,

    @SerializedName("avg_risk_score")
    val avgRiskScore: Double = 0.0,
    @SerializedName("total_risk_score")
    val totalRiskScore: Double = 0.0,

    @SerializedName("route_type_used")
    val routeTypeUsed: String = "",
    val score: Double = 0.0,

    val labels: List<String> = emptyList()
)

data class RouteLeg(
    val origin: String = "",
    val destination: String = "",
    @SerializedName("route_type")
    val routeType: String = "",

    @SerializedName("distance_nm")
    val distanceNm: Double = 0.0,
    @SerializedName("fuel_t")
    val fuelTotalT: Double = 0.0,
    @SerializedName("fuel_cost_usd")
    val fuelCostUsd: Double = 0.0,
    @SerializedName("voyage_days")
    val voyageDays: Double = 0.0,

    @SerializedName("efficiency_score")
    val efficiencyScore: Double = 0.0,
    @SerializedName("composite_risk")
    val compositeRisk: Double = 0.0,

    @SerializedName("storm_risk")
    val stormRisk: Double = 0.0,
    @SerializedName("piracy_risk")
    val piracyRisk: Double = 0.0,
    @SerializedName("total_risk")
    val totalRisk: Double = 0.0,

    @SerializedName("n_records")
    val nRecords: Int = 0
)