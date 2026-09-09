package com.example.marine.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.data.model.Route
import com.example.marine.data.model.VoyageOptions
import com.example.marine.ui.components.MarineDropdown
import com.example.marine.viewmodel.MarineUiState

@Composable
fun HomeScreen(
    uiState: MarineUiState,
    onAnalyzeVoyage: (
        origin: String,
        destination: String,
        shipType: String
    ) -> Unit,
    modifier: Modifier = Modifier
) {

    var origin by rememberSaveable {
        mutableStateOf("")
    }

    var destination by rememberSaveable {
        mutableStateOf("")
    }

    var shipType by rememberSaveable {
        mutableStateOf("")
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        DashboardHeader()

        VoyageSelector(
            origin = origin,
            destination = destination,
            shipType = shipType,

            onOriginChanged = {
                origin = it
            },

            onDestinationChanged = {
                destination = it
            },

            onShipTypeChanged = {
                shipType = it
            },

            onAnalyze = {
                onAnalyzeVoyage(
                    origin,
                    destination,
                    shipType
                )
            },

            isLoading =
                uiState.isLoadingRoutes ||
                        uiState.isLoadingHealth
        )

        HealthCard(
            healthScore = uiState.healthScore,
            alertLevel = uiState.alertLevel,
            isLoading = uiState.isLoadingHealth
        )

        EngineMetricsCard()

        VoyageCard(
            route = uiState.selectedRoute
        )

        RouteSummary(
            routes = uiState.routes
        )

        uiState.healthError?.let {
            Text(
                text = "Health Error: $it",
                color = MaterialTheme.colorScheme.error
            )
        }

        uiState.routeError?.let {
            Text(
                text = "Route Error: $it",
                color = MaterialTheme.colorScheme.error
            )
        }
    }
}

@Composable
private fun DashboardHeader() {
    Column(
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(
            text = "Marine Monitor",
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            text = "Vessel Monitoring System",
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
private fun HealthCard(
    healthScore: Double?,
    alertLevel: String?,
    isLoading: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "VESSEL HEALTH",
                style = MaterialTheme.typography.labelLarge
            )

            if (isLoading) {
                CircularProgressIndicator()
            } else {
                Text(
                    text = healthScore?.let {
                        "%.1f".format(it)
                    } ?: "--",
                    style = MaterialTheme.typography.displaySmall
                )

                Text(
                    text = alertLevel ?: "NO DATA",
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }
    }
}

@Composable
private fun EngineMetricsCard() {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "ENGINE MONITORING",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = "Telemetry data will appear here",
                style = MaterialTheme.typography.bodyLarge
            )

            Text(
                text = "Waiting for vessel telemetry",
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
private fun VoyageCard(
    route: Route?
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "ACTIVE VOYAGE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text("No voyage selected")

            } else {

                Text(
                    text = route.pathStr,
                    style = MaterialTheme.typography.titleMedium
                )

                Text(
                    text = "Distance: %.1f nm"
                        .format(route.totalDistanceNm)
                )

                Text(
                    text = "Voyage: %.1f days"
                        .format(route.totalVoyageDays)
                )

                Text(
                    text = "Fuel: %.1f tonnes"
                        .format(route.totalFuelT)
                )
            }
        }
    }
}

@Composable
private fun RouteSummary(
    routes: List<Route>
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "ROUTE RECOMMENDATIONS",
                style = MaterialTheme.typography.labelLarge
            )

            if (routes.isEmpty()) {

                Text("No route recommendations available")

            } else {

                routes.forEachIndexed { index, route ->

                    Column(
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {

                        Text(
                            text = "Route ${index + 1}",
                            style = MaterialTheme.typography.titleSmall
                        )

                        Text(route.pathStr)

                        Text(
                            text = "Distance: %.1f nm"
                                .format(route.totalDistanceNm)
                        )

                        Text(
                            text = "Fuel: %.1f t"
                                .format(route.totalFuelT)
                        )

                        Text(
                            text = "Risk: %.3f"
                                .format(route.avgRiskScore)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun VoyageSelector(
    origin: String,
    destination: String,
    shipType: String,
    onOriginChanged: (String) -> Unit,
    onDestinationChanged: (String) -> Unit,
    onShipTypeChanged: (String) -> Unit,
    onAnalyze: () -> Unit,
    isLoading: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "SELECT VOYAGE",
                style = MaterialTheme.typography.labelLarge
            )

            MarineDropdown(
                label = "Origin",
                selectedValue = origin,
                options = VoyageOptions.origins,
                onValueSelected = onOriginChanged
            )

            MarineDropdown(
                label = "Destination",
                selectedValue = destination,
                options = VoyageOptions.destinations,
                onValueSelected = onDestinationChanged
            )

            MarineDropdown(
                label = "Ship Type",
                selectedValue = shipType,
                options = VoyageOptions.shipTypes,
                onValueSelected = onShipTypeChanged
            )

            Button(
                onClick = onAnalyze,
                enabled = !isLoading &&
                        origin.isNotBlank() &&
                        destination.isNotBlank() &&
                        shipType.isNotBlank(),
                modifier = Modifier.fillMaxWidth()
            ) {
                if (isLoading) {
                    CircularProgressIndicator()
                } else {
                    Text("Analyze Voyage")
                }
            }
        }
    }
}