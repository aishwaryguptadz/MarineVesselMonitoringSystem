package com.example.marine.ui.analytics

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.viewmodel.MarineUiState

@Composable
fun AnalyticsScreen(
    uiState: MarineUiState,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        Text(
            text = "Analytics",
            style = MaterialTheme.typography.headlineMedium
        )

        HealthAnalyticsCard(uiState)

        VoyageAnalyticsCard(uiState)
    }
}

@Composable
private fun HealthAnalyticsCard(
    uiState: MarineUiState
) {
    Card {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "VESSEL HEALTH",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = uiState.healthScore?.let {
                    "%.1f".format(it)
                } ?: "--",
                style = MaterialTheme.typography.headlineMedium
            )

            Text(
                text = uiState.alertLevel ?: "NO DATA"
            )
        }
    }
}

@Composable
private fun VoyageAnalyticsCard(
    uiState: MarineUiState
) {
    val route = uiState.selectedRoute

    Card {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "VOYAGE PERFORMANCE",
                style = MaterialTheme.typography.labelLarge
            )

            if (route == null) {

                Text("No voyage data available")

            } else {

                Text(
                    text = "Distance: %.1f nm"
                        .format(route.totalDistanceNm)
                )

                Text(
                    text = "Voyage Duration: %.1f days"
                        .format(route.totalVoyageDays)
                )

                Text(
                    text = "Fuel Consumption: %.1f t"
                        .format(route.totalFuelT)
                )

                Text(
                    text = "Fuel Cost: $%,.0f"
                        .format(route.totalFuelCostUsd)
                )

                Text(
                    text = "Risk Score: %.3f"
                        .format(route.avgRiskScore)
                )
            }
        }
    }
}