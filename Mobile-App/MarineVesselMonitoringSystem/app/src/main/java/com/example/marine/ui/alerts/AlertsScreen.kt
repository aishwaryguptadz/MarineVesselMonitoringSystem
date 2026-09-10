package com.example.marine.ui.alerts

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
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
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        Column(
            modifier = Modifier.padding(top = 8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = "Alerts",
                style = MaterialTheme.typography.headlineMedium
            )

            Text(
                text = "Vessel condition and monitoring status",
                style = MaterialTheme.typography.bodyMedium
            )
        }

        CurrentVoyageCard(
            origin = uiState.origin,
            destination = uiState.destination,
            shipType = uiState.shipType
        )

        CurrentStatusCard(
            healthScore = uiState.healthScore,
            alertLevel = uiState.alertLevel
        )

        HealthAssessmentCard(
            healthScore = uiState.healthScore,
            alertLevel = uiState.alertLevel
        )

        MonitoringStatusCard()

        uiState.healthError?.let { error ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    text = "Health monitoring error: $error",
                    modifier = Modifier.padding(20.dp),
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun CurrentStatusCard(
    healthScore: Double?,
    alertLevel: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "CURRENT STATUS",
                style = MaterialTheme.typography.labelLarge
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {

                Text(
                    text = alertLevel ?: "NO DATA",
                    style = MaterialTheme.typography.headlineSmall
                )

                Text(
                    text = healthScore?.let {
                        "%.1f".format(it)
                    } ?: "--",
                    style = MaterialTheme.typography.headlineSmall
                )
            }

            Text(
                text = statusDescription(alertLevel),
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

private fun statusDescription(
    alertLevel: String?
): String {
    return when (alertLevel) {

        "HEALTHY" ->
            "Vessel is operating within the healthy range."

        "WARNING" ->
            "Vessel condition requires monitoring."

        "CRITICAL" ->
            "Vessel health is in a critical state and requires attention."

        else ->
            "No vessel health information is currently available."
    }
}

@Composable
private fun HealthAssessmentCard(
    healthScore: Double?,
    alertLevel: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "HEALTH ASSESSMENT",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = "Health Score",
                style = MaterialTheme.typography.bodyMedium
            )

            Text(
                text = healthScore?.let {
                    "%.1f / 100".format(it)
                } ?: "--",
                style = MaterialTheme.typography.headlineSmall
            )

            Text(
                text = assessmentMessage(
                    healthScore,
                    alertLevel
                ),
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

private fun assessmentMessage(
    healthScore: Double?,
    alertLevel: String?
): String {

    if (healthScore == null) {
        return "Health assessment unavailable."
    }

    return when (alertLevel) {

        "HEALTHY" ->
            "No immediate health concern detected."

        "WARNING" ->
            "The vessel should be monitored for developing issues."

        "CRITICAL" ->
            "The current prediction indicates a critical vessel condition."

        else ->
            "Health status: %.1f".format(healthScore)
    }
}

@Composable
private fun MonitoringStatusCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "MONITORING STATUS",
                style = MaterialTheme.typography.labelLarge
            )

            MonitoringRow(
                label = "Route monitoring",
                status = "Active"
            )

            MonitoringRow(
                label = "Health monitoring",
                status = "Active"
            )

            MonitoringRow(
                label = "Engine telemetry",
                status = "Pending"
            )
        }
    }
}

@Composable
private fun MonitoringRow(
    label: String,
    status: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {

        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium
        )

        Text(
            text = status,
            style = MaterialTheme.typography.labelLarge
        )
    }
}

@Composable
private fun CurrentVoyageCard(
    origin: String,
    destination: String,
    shipType: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "CURRENT VOYAGE",
                style = MaterialTheme.typography.labelLarge
            )

            if (
                origin.isBlank() ||
                destination.isBlank()
            ) {
                Text("No voyage selected")
            } else {

                Text(
                    text = "$origin → $destination",
                    style = MaterialTheme.typography.titleLarge
                )

                if (shipType.isNotBlank()) {
                    Text(
                        text = shipType
                    )
                }
            }
        }
    }
}