
package com.example.marine.ui.assistant

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.data.model.AskAnalysis
import com.example.marine.viewmodel.MarineUiState

@Composable
fun AssistantScreen(
    uiState: MarineUiState,
    onAskQuestion: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var question by rememberSaveable {
        mutableStateOf("")
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {

            IconButton(
                onClick = onBack
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Text(
                    text = "AI Assistant",
                    style = MaterialTheme.typography.headlineSmall
                )

                Text(
                    text = "Marine Vessel Intelligence",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Surface(
                shape = RoundedCornerShape(14.dp),
                color = MaterialTheme.colorScheme.primaryContainer
            ) {
                Icon(
                    imageVector = Icons.Default.AutoAwesome,
                    contentDescription = null,
                    modifier = Modifier.padding(10.dp),
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(18.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {

                Text(
                    text = "How can I help?",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )

                Text(
                    text = "Ask about vessel health, route performance, fuel consumption or voyage risks.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }

        CurrentVoyageCard(uiState)

        SuggestedQuestions(
            onQuestionSelected = {
                question = it
            }
        )

        Column(
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {

            Text(
                text = "ASK YOUR QUESTION",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            OutlinedTextField(
                value = question,
                onValueChange = {
                    question = it
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 100.dp),
                placeholder = {
                    Text(
                        "e.g. How can I reduce fuel consumption?"
                    )
                },
                maxLines = 4,
                shape = RoundedCornerShape(16.dp)
            )

            Button(
                onClick = {
                    onAskQuestion(question.trim())
                },
                enabled = question.isNotBlank() &&
                        !uiState.isLoadingAssistant,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp)
            ) {

                if (uiState.isLoadingAssistant) {
                    CircularProgressIndicator(
                        modifier = Modifier
                            .padding(end = 8.dp),
                        strokeWidth = 2.dp
                    )
                }

                Text(
                    text = if (uiState.isLoadingAssistant) {
                        "Analyzing..."
                    } else {
                        "Ask Assistant"
                    }
                )
            }
        }

        // ---------------------------------------------------------
        // ERROR
        // ---------------------------------------------------------

        uiState.assistantError?.let {
            ErrorCard(it)
        }

        // ---------------------------------------------------------
        // RESPONSE
        // ---------------------------------------------------------

        uiState.assistantAnalysis?.let { analysis ->

            AssistantResponseCard(
                question = uiState.assistantQuestion,
                analysis = analysis,
                rootCauses = uiState.rootCauses,
                report = uiState.assistantReport
            )
        }

        // Bottom spacing
        androidx.compose.foundation.layout.Spacer(
            modifier = Modifier.padding(bottom = 20.dp)
        )
    }
}

@Composable
private fun CurrentVoyageCard(
    uiState: MarineUiState
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp)
    ) {

        Column(
            modifier = Modifier.padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            Text(
                text = "CURRENT VOYAGE",
                style = MaterialTheme.typography.labelMedium,
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
                    text = "Select a voyage from Home to give the assistant more context.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

            } else {

                Text(
                    text = "${uiState.origin} → ${uiState.destination}",
                    style = MaterialTheme.typography.titleMedium
                )

                if (uiState.shipType.isNotBlank()) {

                    Surface(
                        shape = RoundedCornerShape(50.dp),
                        color = MaterialTheme.colorScheme.secondaryContainer
                    ) {
                        Text(
                            text = uiState.shipType,
                            modifier = Modifier.padding(
                                horizontal = 10.dp,
                                vertical = 5.dp
                            ),
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SuggestedQuestions(
    onQuestionSelected: (String) -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {

        Text(
            text = "TRY ASKING",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        val questions = listOf(
            "Why is the vessel health critical?",
            "Explain the recommended route",
            "What are the major voyage risks?",
            "How can I reduce fuel consumption?"
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            SuggestionCard(
                text = questions[0],
                modifier = Modifier.weight(1f),
                onClick = {
                    onQuestionSelected(questions[0])
                }
            )

            SuggestionCard(
                text = questions[1],
                modifier = Modifier.weight(1f),
                onClick = {
                    onQuestionSelected(questions[1])
                }
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            SuggestionCard(
                text = questions[2],
                modifier = Modifier.weight(1f),
                onClick = {
                    onQuestionSelected(questions[2])
                }
            )

            SuggestionCard(
                text = questions[3],
                modifier = Modifier.weight(1f),
                onClick = {
                    onQuestionSelected(questions[3])
                }
            )
        }
    }
}

@Composable
private fun SuggestionCard(
    text: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(14.dp),
            style = MaterialTheme.typography.bodySmall
        )
    }
}

@Composable
private fun AssistantResponseCard(
    question: String?,
    analysis: AskAnalysis,
    rootCauses: List<String>,
    report: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {

        Column(
            modifier = Modifier.padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {

                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = MaterialTheme.colorScheme.primaryContainer
                ) {
                    Icon(
                        imageVector = Icons.Default.AutoAwesome,
                        contentDescription = null,
                        modifier = Modifier.padding(7.dp),
                        tint = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }

                Text(
                    text = "AI ANALYSIS",
                    style = MaterialTheme.typography.titleMedium
                )
            }

            if (!question.isNullOrBlank()) {

                Text(
                    text = question,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Text(
                text = "Operational metrics",
                style = MaterialTheme.typography.titleSmall
            )

            MetricRow(
                "Carbon emission",
                analysis.avgCarbonEmission
            )

            MetricRow(
                "Fuel consumption",
                analysis.avgFuelConsumption
            )

            MetricRow(
                "Engine load",
                analysis.avgEngineLoad,
                "%"
            )

            MetricRow(
                "Average speed",
                analysis.avgSpeed
            )

            MetricRow(
                "Wave height",
                analysis.avgWaveHeight
            )

            MetricRow(
                "Wind speed",
                analysis.avgWindSpeed
            )

            if (rootCauses.isNotEmpty()) {

                Text(
                    text = "ROOT CAUSES",
                    style = MaterialTheme.typography.titleSmall
                )

                rootCauses.forEachIndexed { index, cause ->

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        verticalAlignment = Alignment.Top
                    ) {

                        Text(
                            text = "${index + 1}",
                            color = MaterialTheme.colorScheme.primary,
                            style = MaterialTheme.typography.labelLarge
                        )

                        Text(
                            text = cause,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            if (!report.isNullOrBlank()) {

                Text(
                    text = "REPORT",
                    style = MaterialTheme.typography.titleSmall
                )

                Text(
                    text = report,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun MetricRow(
    label: String,
    value: Double?,
    unit: String = ""
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {

        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Text(
            text = value?.let {
                "%.2f%s".format(it, unit)
            } ?: "--",
            style = MaterialTheme.typography.labelLarge
        )
    }
}

@Composable
private fun ErrorCard(
    error: String
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
                text = "Analysis unavailable",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )

            Text(
                text = error,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
        }
    }
}
