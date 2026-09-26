package com.example.marine.ui.map

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.example.marine.data.model.Route
import com.example.marine.viewmodel.MarineUiState

@Composable
fun MapScreen(
    uiState: MarineUiState,
    onRouteSelected: (Route) -> Unit,
    modifier: Modifier = Modifier
) {
    val selectedRoute = uiState.selectedRoute

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        item {
            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Route Map",
                style = MaterialTheme.typography.headlineMedium
            )

            Text(
                text = "Voyage route and recommendations",
                style = MaterialTheme.typography.bodyMedium
            )
        }

        item {
            RouteVisualization(
                route = selectedRoute
            )
        }

        item {
            VoyageSummary(
                route = selectedRoute
            )
        }

        item {
            Text(
                text = "ROUTE RECOMMENDATIONS",
                style = MaterialTheme.typography.labelLarge
            )
        }

        itemsIndexed(uiState.routes) { index, route ->

            RouteOptionCard(
                routeNumber = index + 1,
                route = route,
                selected = route == selectedRoute,
                onClick = {
                    onRouteSelected(route)
                }
            )
        }

        item {
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun RouteVisualization(
    route: Route?
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {

            Text(
                text = "ACTIVE ROUTE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text(
                    text = "No route selected",
                    style = MaterialTheme.typography.bodyLarge
                )

            } else {

                if (route.labels.isNotEmpty()) {
                    Text(
                        text = route.labels.joinToString(" • "),
                        style = MaterialTheme.typography.labelMedium
                    )
                }

                Text(
                    text = route.pathStr,
                    style = MaterialTheme.typography.titleMedium
                )

                RoutePath(
                    route = route
                )
            }
        }
    }
}

@Composable
private fun RoutePath(
    route: Route
) {
    Column(
        modifier = Modifier.fillMaxWidth()
    ) {

        route.path.forEachIndexed { index, location ->

            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {

                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {

                    Box(
                        modifier = Modifier
                            .size(14.dp)
                            .clip(CircleShape)
                            .background(
                                MaterialTheme.colorScheme.primary
                            )
                    )

                    if (index < route.path.lastIndex) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .height(45.dp)
                                .background(
                                    MaterialTheme.colorScheme.primary
                                )
                        )
                    }
                }

                Spacer(
                    modifier = Modifier.width(12.dp)
                )

                Text(
                    text = location,
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
    }
}

@Composable
private fun VoyageSummary(
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
                text = "VOYAGE SUMMARY",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text("No voyage data available")

            } else {

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    SummaryMetric(
                        label = "Distance",
                        value = "%.1f nm"
                            .format(route.totalDistanceNm)
                    )

                    SummaryMetric(
                        label = "Duration",
                        value = "%.1f days"
                            .format(route.totalVoyageDays)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    SummaryMetric(
                        label = "Fuel",
                        value = "%.1f t"
                            .format(route.totalFuelT)
                    )

                    SummaryMetric(
                        label = "Risk",
                        value = "%.3f"
                            .format(route.avgRiskScore)
                    )
                }

                SummaryMetric(
                    label = "Estimated Fuel Cost",
                    value = "$%,.0f"
                        .format(route.totalFuelCostUsd)
                )
            }
        }
    }
}

@Composable
private fun SummaryMetric(
    label: String,
    value: String
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(2.dp)
    ) {

        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium
        )

        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium
        )
    }
}

@Composable
private fun RouteOptionCard(
    routeNumber: Int,
    route: Route,
    selected: Boolean,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {

                Text(
                    text = "Route $routeNumber",
                    style = MaterialTheme.typography.titleMedium
                )

                if (selected) {
                    Text(
                        text = "SELECTED",
                        style = MaterialTheme.typography.labelMedium
                    )
                }
            }

            if (route.labels.isNotEmpty()) {
                Text(
                    text = route.labels.joinToString(" • "),
                    style = MaterialTheme.typography.labelMedium
                )
            }

            Text(
                text = route.pathStr
            )

            Text(
                text = "%.1f nm • %.1f days • %.1f t fuel"
                    .format(
                        route.totalDistanceNm,
                        route.totalVoyageDays,
                        route.totalFuelT
                    ),
                style = MaterialTheme.typography.bodyMedium
            )

            Text(
                text = "Risk: %.3f"
                    .format(route.avgRiskScore),
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}