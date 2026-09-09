package com.example.marine.ui.alerts

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
fun AlertsScreen(
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
            text = "Alerts",
            style = MaterialTheme.typography.headlineMedium
        )

        AlertCard(uiState)
    }
}

@Composable
private fun AlertCard(
    uiState: MarineUiState
) {
    Card {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "CURRENT VESSEL STATUS",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = uiState.alertLevel ?: "NO DATA",
                style = MaterialTheme.typography.titleLarge
            )

            when (uiState.alertLevel) {

                "CRITICAL" -> {
                    Text(
                        text = "Immediate attention required."
                    )
                }

                "WARNING" -> {
                    Text(
                        text = "Vessel requires monitoring."
                    )
                }

                "HEALTHY" -> {
                    Text(
                        text = "No active health alerts."
                    )
                }

                else -> {
                    Text(
                        text = "No vessel health information available."
                    )
                }
            }
        }
    }
}