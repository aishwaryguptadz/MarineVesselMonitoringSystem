package com.example.marine.ui.map

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.viewmodel.MarineUiState

@Composable
fun MapScreen(
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
            text = "Route Map",
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            text = "Voyage Route",
            style = MaterialTheme.typography.labelLarge
        )

        val route = uiState.selectedRoute

        if (route == null) {

            Text(
                text = "No route selected",
                style = MaterialTheme.typography.bodyLarge
            )

        } else {

            Text(
                text = route.pathStr,
                style = MaterialTheme.typography.titleLarge
            )

            Text(
                text = "Distance: %.1f nm"
                    .format(route.totalDistanceNm)
            )

            Text(
                text = "Estimated voyage: %.1f days"
                    .format(route.totalVoyageDays)
            )

            Text(
                text = "Route visualization will appear here."
            )
        }
    }
}