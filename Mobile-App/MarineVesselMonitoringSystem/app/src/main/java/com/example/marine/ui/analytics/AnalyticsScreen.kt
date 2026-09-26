package com.example.marine.ui.analytics

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.data.model.Route
import com.example.marine.viewmodel.MarineUiState

@Composable
fun AnalyticsScreen(
    uiState: MarineUiState,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        item {
            Column(
                modifier = Modifier.padding(top = 8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "Analytics",
                    style = MaterialTheme.typography.headlineMedium
                )

                Text(
                    text = "Selected voyage performance",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }

        item {
            HealthAnalyticsCard(
                healthScore = uiState.healthScore,
                alertLevel = uiState.alertLevel
            )
        }

        item {
            VoyagePerformanceCard(
                route = uiState.selectedRoute
            )
        }

        item {
            RiskCard(
                route = uiState.selectedRoute
            )
        }

        item {
            SelectedRouteCard(
                route = uiState.selectedRoute
            )
        }

        item {
            Spacer(
                modifier = Modifier.height(16.dp)
            )
        }
    }
}

@Composable
private fun HealthAnalyticsCard(
    healthScore: Double?,
    alertLevel: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "VESSEL HEALTH",
                style = MaterialTheme.typography.labelLarge
            )

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

@Composable
private fun VoyagePerformanceCard(
    route: Route?
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "VOYAGE PERFORMANCE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text("No voyage selected")

            } else {

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {

                    MetricCard(
                        label = "DISTANCE",
                        value = "%.1f nm"
                            .format(route.totalDistanceNm),
                        modifier = Modifier.weight(1f)
                    )

                    MetricCard(
                        label = "DURATION",
                        value = "%.1f days"
                            .format(route.totalVoyageDays),
                        modifier = Modifier.weight(1f)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {

                    MetricCard(
                        label = "FUEL",
                        value = "%.1f t"
                            .format(route.totalFuelT),
                        modifier = Modifier.weight(1f)
                    )

                    MetricCard(
                        label = "FUEL COST",
                        value = "$%,.0f"
                            .format(route.totalFuelCostUsd),
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
private fun MetricCard(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {

            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall
            )

            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}

@Composable
private fun RiskCard(
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
                text = "RISK PROFILE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text("No route selected")

            } else {

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    Text("Average Risk")

                    Text(
                        text = "%.3f"
                            .format(route.avgRiskScore),
                        style = MaterialTheme.typography.titleMedium
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    Text("Total Risk")

                    Text(
                        text = "%.3f"
                            .format(route.totalRiskScore),
                        style = MaterialTheme.typography.titleMedium
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    Text("Route Type")

                    Text(
                        text = route.routeTypeUsed,
                        style = MaterialTheme.typography.titleMedium
                    )
                }
            }
        }
    }
}

@Composable
private fun SelectedRouteCard(
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
                text = "SELECTED ROUTE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text(
                    text = "No route selected",
                    style = MaterialTheme.typography.bodyLarge
                )

            } else {

                Text(
                    text = route.pathStr,
                    style = MaterialTheme.typography.titleMedium
                )

                if (route.labels.isNotEmpty()) {
                    Text(
                        text = route.labels.joinToString(" • "),
                        style = MaterialTheme.typography.labelMedium
                    )
                }

                Text(
                    text = "Route type: ${route.routeTypeUsed}"
                )
            }
        }
    }
}