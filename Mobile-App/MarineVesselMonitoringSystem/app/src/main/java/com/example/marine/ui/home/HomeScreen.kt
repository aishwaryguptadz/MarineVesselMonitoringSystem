
package com.example.marine.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
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
import com.example.marine.ui.components.MetricCard
import com.example.marine.ui.components.SectionHeader
import com.example.marine.ui.components.StatusChip
import com.example.marine.ui.components.StatusType
import com.example.marine.ui.theme.Fuel
import com.example.marine.ui.theme.Speed
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
    var origin by rememberSaveable { mutableStateOf("") }
    var destination by rememberSaveable { mutableStateOf("") }
    var shipType by rememberSaveable { mutableStateOf("") }

    val isLoading = uiState.isLoadingRoutes || uiState.isLoadingHealth

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(22.dp)
    ) {
        DashboardHeader()

        SectionHeader(
            title = "Vessel health",
            subtitle = "Latest available health assessment"
        )

        HealthOverview(
            healthScore = uiState.healthScore,
            alertLevel = uiState.alertLevel,
            isLoading = uiState.isLoadingHealth
        )

        SectionHeader(
            title = "Plan a voyage",
            subtitle = "Choose a route to view its estimated performance"
        )

        VoyageSelector(
            origin = origin,
            destination = destination,
            shipType = shipType,
            onOriginChanged = { origin = it },
            onDestinationChanged = { destination = it },
            onShipTypeChanged = { shipType = it },
            onAnalyze = {
                onAnalyzeVoyage(origin, destination, shipType)
            },
            isLoading = isLoading
        )

        SectionHeader(
            title = "Engine monitoring",
            subtitle = "Telemetry metrics"
        )

        EngineMetricsCard()

        SectionHeader(
            title = "Selected voyage",
            subtitle = "Summary of the currently selected route"
        )

        SelectedVoyageCard(route = uiState.selectedRoute)

        SectionHeader(
            title = "Route recommendations",
            subtitle = "${uiState.routes.size} route(s) available"
        )

        RouteSummary(routes = uiState.routes)

        uiState.healthError?.let {
            ErrorCard(title = "Health data unavailable", message = it)
        }

        uiState.routeError?.let {
            ErrorCard(title = "Route analysis failed", message = it)
        }

        Spacer(modifier = Modifier.height(8.dp))
    }
}

@Composable
private fun DashboardHeader() {
    Column(
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text(
            text = "Marine Monitor",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onBackground
        )

        Text(
            text = "Vessel Monitoring System",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun HealthOverview(
    healthScore: Double?,
    alertLevel: String?,
    isLoading: Boolean
) {
    val status = when (alertLevel.orEmpty().uppercase()) {
        "HEALTHY", "NORMAL", "LOW" -> StatusType.HEALTHY
        "WARNING", "MEDIUM", "MODERATE" -> StatusType.WARNING
        "CRITICAL", "HIGH", "DANGER" -> StatusType.CRITICAL
        else -> StatusType.OFFLINE
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "OVERALL HEALTH SCORE",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            if (isLoading) {
                CircularProgressIndicator()
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = healthScore?.let { "%.1f".format(it) } ?: "--",
                        style = MaterialTheme.typography.displayMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )

                    StatusChip(
                        label = alertLevel ?: "No data",
                        status = status
                    )
                }

                Text(
                    text = if (healthScore != null) {
                        "Based on the latest health assessment"
                    } else {
                        "Health information is not available yet"
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EngineMetricsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Telemetry is not available",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "Engine speed, temperature, vibration and load metrics " +
                        "will be displayed here when telemetry data is connected.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun SelectedVoyageCard(route: Route?) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        if (route == null) {
            Text(
                text = "No voyage selected. Analyze a voyage to see its summary here.",
                modifier = Modifier.padding(18.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        } else {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Text(
                    text = route.pathStr.ifBlank { "Selected route" },
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    MetricCard(
                        title = "Distance",
                        value = "%.1f".format(route.totalDistanceNm),
                        unit = "nm",
                        modifier = Modifier.weight(1f),
                        accentColor = Speed
                    )

                    MetricCard(
                        title = "Duration",
                        value = "%.1f".format(route.totalVoyageDays),
                        unit = "days",
                        modifier = Modifier.weight(1f),
                        accentColor = MaterialTheme.colorScheme.primary
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    MetricCard(
                        title = "Fuel estimate",
                        value = "%.1f".format(route.totalFuelT),
                        unit = "t",
                        modifier = Modifier.weight(1f),
                        accentColor = Fuel
                    )

                    MetricCard(
                        title = "Average risk",
                        value = "%.3f".format(route.avgRiskScore),
                        modifier = Modifier.weight(1f),
                        accentColor = MaterialTheme.colorScheme.error
                    )
                }
            }
        }
    }
}

@Composable
private fun RouteSummary(routes: List<Route>) {
    if (routes.isEmpty()) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Text(
                text = "No route recommendations yet. Select an origin, " +
                        "destination and ship type to analyze a voyage.",
                modifier = Modifier.padding(18.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    } else {
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            routes.forEachIndexed { index, route ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    )
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Route ${index + 1}",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurface
                        )

                        Text(
                            text = route.pathStr.ifBlank { "Route details unavailable" },
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        Text(
                            text = "${"%.1f".format(route.totalDistanceNm)} nm  •  " +
                                    "${"%.1f".format(route.totalFuelT)} t fuel  •  " +
                                    "${"%.3f".format(route.avgRiskScore)} risk",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
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
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
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

@Composable
private fun ErrorCard(
    title: String,
    message: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
        }
    }
}