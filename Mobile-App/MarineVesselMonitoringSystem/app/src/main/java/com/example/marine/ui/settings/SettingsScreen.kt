package com.example.marine.ui.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.viewmodel.MarineUiState

@Composable
fun SettingsScreen(
    uiState: MarineUiState,
    onResetVoyage: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        Column(
            modifier = Modifier.padding(top = 8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = "Settings",
                style = MaterialTheme.typography.headlineMedium
            )

            Text(
                text = "Application and voyage configuration",
                style = MaterialTheme.typography.bodyMedium
            )
        }

        CurrentVoyageCard(
            uiState = uiState
        )

        ConnectionCard(
            uiState = uiState
        )

        ApplicationCard()

        Button(
            onClick = onResetVoyage,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Reset Current Voyage")
        }
    }
}

@Composable
private fun CurrentVoyageCard(
    uiState: MarineUiState
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "CURRENT VOYAGE",
                style = MaterialTheme.typography.labelLarge
            )

            if (
                uiState.origin.isBlank() ||
                uiState.destination.isBlank()
            ) {

                Text(
                    text = "No voyage selected"
                )

            } else {

                Text(
                    text = "${uiState.origin} → ${uiState.destination}",
                    style = MaterialTheme.typography.titleLarge
                )

                Text(
                    text = if (uiState.shipType.isNotBlank()) {
                        uiState.shipType
                    } else {
                        "Ship type not specified"
                    }
                )
            }
        }
    }
}

@Composable
private fun ConnectionCard(
    uiState: MarineUiState
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "CONNECTION",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = when {
                    uiState.connectionStatus != null ->
                        "Backend connected"

                    uiState.connectionError != null ->
                        "Backend connection failed"

                    else ->
                        "Connection not tested"
                },
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}

@Composable
private fun ApplicationCard() {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "APPLICATION",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = "Marine Vessel Monitoring",
                style = MaterialTheme.typography.titleMedium
            )

            Text(
                text = "Version 1.0"
            )

            Text(
                text = "Android application for maritime route and vessel monitoring."
            )
        }
    }
}