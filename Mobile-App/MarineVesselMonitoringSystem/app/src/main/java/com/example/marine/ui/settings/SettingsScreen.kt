package com.example.marine.ui.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
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
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        CurrentVoyageCard(uiState)

        ConnectionCard(uiState)

        ApplicationCard()

        Button(
            onClick = onResetVoyage,
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp)
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
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "CURRENT VOYAGE",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            if (
                uiState.origin.isBlank() ||
                uiState.destination.isBlank()
            ) {
                Text(
                    text = "No voyage selected",
                    style = MaterialTheme.typography.titleMedium
                )

                Text(
                    text = "Select a voyage from the Home screen.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                Text(
                    text = "${uiState.origin} → ${uiState.destination}",
                    style = MaterialTheme.typography.titleLarge
                )

                Surface(
                    shape = RoundedCornerShape(50),
                    color = MaterialTheme.colorScheme.primaryContainer
                ) {
                    Text(
                        text = if (uiState.shipType.isNotBlank()) {
                            uiState.shipType
                        } else {
                            "Ship type not specified"
                        },
                        modifier = Modifier.padding(
                            horizontal = 12.dp,
                            vertical = 7.dp
                        ),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }
    }
}

@Composable
private fun ConnectionCard(
    uiState: MarineUiState
) {
    val connectionState = when {
        uiState.isTestingConnection -> ConnectionState.TESTING

        uiState.connectionError != null -> ConnectionState.ERROR

        uiState.connectionStatus != null -> ConnectionState.CONNECTED

        else -> ConnectionState.NOT_TESTED
    }

    val statusColor = when (connectionState) {
        ConnectionState.CONNECTED -> Color(0xFF2E7D32)
        ConnectionState.ERROR -> MaterialTheme.colorScheme.error
        ConnectionState.TESTING -> MaterialTheme.colorScheme.primary
        ConnectionState.NOT_TESTED -> MaterialTheme.colorScheme.outline
    }

    val statusText = when (connectionState) {
        ConnectionState.CONNECTED -> "Connected"
        ConnectionState.ERROR -> "Connection failed"
        ConnectionState.TESTING -> "Testing connection"
        ConnectionState.NOT_TESTED -> "Not tested"
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {

            Text(
                text = "CONNECTION",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "Backend service",
                        style = MaterialTheme.typography.titleMedium
                    )

                    Text(
                        text = when (connectionState) {
                            ConnectionState.CONNECTED ->
                                uiState.connectionStatus ?: "Backend is reachable"

                            ConnectionState.ERROR ->
                                uiState.connectionError ?: "Unable to reach backend"

                            ConnectionState.TESTING ->
                                "Checking backend availability..."

                            ConnectionState.NOT_TESTED ->
                                "Connection has not been tested yet"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Surface(
                    shape = RoundedCornerShape(50),
                    color = statusColor.copy(alpha = 0.12f)
                ) {
                    Text(
                        text = statusText,
                        modifier = Modifier.padding(
                            horizontal = 10.dp,
                            vertical = 6.dp
                        ),
                        color = statusColor,
                        style = MaterialTheme.typography.labelMedium
                    )
                }
            }
        }
    }
}

@Composable
private fun ApplicationCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "APPLICATION",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Text(
                text = "Marine Vessel Monitoring",
                style = MaterialTheme.typography.titleLarge
            )

            Text(
                text = "Version 2.0",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.primary
            )

            Text(
                text = "Android application for maritime route and vessel monitoring.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private enum class ConnectionState {
    CONNECTED,
    ERROR,
    TESTING,
    NOT_TESTED
}