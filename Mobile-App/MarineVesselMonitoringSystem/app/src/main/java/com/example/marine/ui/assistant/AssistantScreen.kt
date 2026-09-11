package com.example.marine.ui.assistant

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
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
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {

            IconButton(
                onClick = onBack
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }

            Column {
                Text(
                    text = "AI Assistant",
                    style = MaterialTheme.typography.headlineMedium
                )

                Text(
                    text = "Marine Vessel Intelligence",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }

        CurrentVoyageCard(uiState)

        SuggestedQuestions(
            onQuestionSelected = { question = it }
        )

        OutlinedTextField(
            value = question,
            onValueChange = { question = it },
            modifier = Modifier.fillMaxWidth(),
            label = {
                Text("Ask a question")
            },
            placeholder = {
                Text("Ask about vessel health, routes or risks")
            },
            minLines = 3,
            maxLines = 5
        )

        Button(
            onClick = {
                onAskQuestion(question.trim())
            },
            enabled = question.isNotBlank() &&
                    !uiState.isLoadingAssistant,
            modifier = Modifier.fillMaxWidth()
        ) {

            if (uiState.isLoadingAssistant) {
                CircularProgressIndicator(
                    strokeWidth = 2.dp,
                    modifier = Modifier.padding(end = 8.dp)
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

        uiState.assistantError?.let { error ->
            ErrorCard(error)
        }

        uiState.assistantAnalysis?.let {
            AssistantResponseCard(
                answer = uiState.assistantAnalysis.toString(),
                rootCauses = uiState.rootCauses,
                report = uiState.assistantReport
            )
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
            verticalArrangement = Arrangement.spacedBy(8.dp)
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
                    style = MaterialTheme.typography.titleMedium
                )

                if (uiState.shipType.isNotBlank()) {
                    Text(
                        text = uiState.shipType,
                        style = MaterialTheme.typography.bodyMedium
                    )
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
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {

        Text(
            text = "SUGGESTED QUESTIONS",
            style = MaterialTheme.typography.labelLarge
        )

        listOf(
            "Why is the vessel health critical?",
            "Explain the recommended route",
            "What are the major voyage risks?",
            "How can I reduce fuel consumption?"
        ).forEach { question ->

            Card(
                onClick = {
                    onQuestionSelected(question)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = question,
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
}

@Composable
private fun AssistantResponseCard(
    answer: String,
    rootCauses: List<String>,
    report: String?
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {

            Text(
                text = "AI ANALYSIS",
                style = MaterialTheme.typography.labelLarge
            )

            Text(
                text = answer,
                style = MaterialTheme.typography.bodyLarge
            )

            if (rootCauses.isNotEmpty()) {

                Text(
                    text = "ROOT CAUSES",
                    style = MaterialTheme.typography.labelLarge
                )

                rootCauses.forEach { cause ->
                    Text(
                        text = "• $cause"
                    )
                }
            }

            if (!report.isNullOrBlank()) {

                Text(
                    text = "REPORT",
                    style = MaterialTheme.typography.labelLarge
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
private fun ErrorCard(
    error: String
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = error,
            color = MaterialTheme.colorScheme.error,
            modifier = Modifier.padding(20.dp)
        )
    }
}