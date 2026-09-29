
package com.example.marine.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = OceanBlue,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD9EDF4),
    onPrimaryContainer = OceanBlueDark,

    secondary = Aqua,
    onSecondary = Navy,
    secondaryContainer = Color(0xFFD5F3EF),
    onSecondaryContainer = Color(0xFF124B49),

    tertiary = Navy,
    onTertiary = Color.White,

    background = BackgroundLight,
    onBackground = TextPrimaryLight,

    surface = SurfaceLight,
    onSurface = TextPrimaryLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = TextSecondaryLight,

    outline = OutlineLight,
    error = Error,
    onError = Color.White
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF70C4DE),
    onPrimary = Color(0xFF073747),
    primaryContainer = Color(0xFF15536A),
    onPrimaryContainer = Color(0xFFD2F2FC),

    secondary = Color(0xFF69D2C8),
    onSecondary = Color(0xFF073B37),
    secondaryContainer = Color(0xFF205A55),
    onSecondaryContainer = Color(0xFFC8F4EE),

    tertiary = Color(0xFFB7C9F7),
    onTertiary = Color(0xFF25375C),

    background = BackgroundDark,
    onBackground = TextPrimaryDark,

    surface = SurfaceDark,
    onSurface = TextPrimaryDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = TextSecondaryDark,

    outline = OutlineDark,
    error = Color(0xFFFF8A80),
    onError = Color(0xFF5F1111)
)

@Composable
fun MarineTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) {
            DarkColorScheme
        } else {
            LightColorScheme
        },
        typography = Typography,
        content = content
    )
}