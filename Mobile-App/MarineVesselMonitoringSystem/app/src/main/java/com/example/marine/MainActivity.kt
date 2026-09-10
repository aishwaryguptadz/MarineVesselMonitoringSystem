package com.example.marine

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.marine.ui.alerts.AlertsScreen
import com.example.marine.ui.analytics.AnalyticsScreen
import com.example.marine.ui.home.HomeScreen
import com.example.marine.ui.map.MapScreen
import com.example.marine.ui.settings.SettingsScreen
import com.example.marine.ui.theme.MarineTheme
import com.example.marine.viewmodel.MarineViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MarineTheme {
                MarineApp()
            }
        }
    }
}


@Composable
fun MarineApp(
    viewModel: MarineViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    var currentDestination by rememberSaveable {
        mutableStateOf(AppDestinations.HOME)
    }

    NavigationSuiteScaffold(
        navigationSuiteItems = {
            AppDestinations.entries.forEach {
                item(
                    icon = {
                        Icon(
                            imageVector = it.icon,
                            contentDescription = it.label
                        )
                    },
                    label = {
                        Text(it.label)
                    },
                    selected = it == currentDestination,
                    onClick = {
                        currentDestination = it
                    }
                )
            }
        }
    ) {
        Scaffold(
            modifier = Modifier.fillMaxSize()
        ) { innerPadding ->

            when (currentDestination) {

                AppDestinations.HOME -> {
                    HomeScreen(
                        uiState = uiState,
                        onAnalyzeVoyage = { origin, destination, shipType ->

                            viewModel.analyzeVoyage(
                                origin = origin,
                                destination = destination,
                                shipType = shipType
                            )
                        },
                        modifier = Modifier.padding(innerPadding)
                    )
                }

                AppDestinations.MAP -> {
                    MapScreen(
                        uiState = uiState,
                        onRouteSelected = { route ->
                            viewModel.selectRoute(route)
                        },
                        modifier = Modifier.padding(innerPadding)
                    )
                }

                AppDestinations.ANALYTICS -> {
                    AnalyticsScreen(
                        uiState = uiState,
                        modifier = Modifier.padding(innerPadding)
                    )
                }

                AppDestinations.ALERTS -> {
                    AlertsScreen(
                        uiState = uiState,
                        modifier = Modifier.padding(innerPadding)
                    )
                }

                AppDestinations.SETTINGS -> {
                    SettingsScreen(
                        uiState = uiState,

                        onResetVoyage = {
                            viewModel.resetVoyage()
                        },

                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

enum class AppDestinations(
    val label: String,
    val icon: ImageVector
) {

    HOME(
        label = "Home",
        icon = Icons.Default.Home
    ),

    MAP(
        label = "Map",
        icon = Icons.Default.Map
    ),

    ANALYTICS(
        label = "Analytics",
        icon = Icons.Default.Analytics
    ),

    ALERTS(
        label = "Alerts",
        icon = Icons.Default.Notifications
    ),

    SETTINGS(
        label = "Settings",
        icon = Icons.Default.Settings
    )
}

@Preview
@Composable
fun Preview() {
    MarineApp()
}