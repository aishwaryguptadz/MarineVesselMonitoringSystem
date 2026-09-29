
package com.example.marine.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.marine.ui.theme.Error
import com.example.marine.ui.theme.Offline
import com.example.marine.ui.theme.Success
import com.example.marine.ui.theme.Warning

enum class StatusType {
    HEALTHY,
    WARNING,
    CRITICAL,
    OFFLINE
}

@Composable
fun StatusChip(
    label: String,
    status: StatusType,
    modifier: Modifier = Modifier
) {
    val statusColor = when (status) {
        StatusType.HEALTHY -> Success
        StatusType.WARNING -> Warning
        StatusType.CRITICAL -> Error
        StatusType.OFFLINE -> Offline
    }

    Row(
        modifier = modifier
            .background(
                color = statusColor.copy(alpha = 0.12f),
                shape = RoundedCornerShape(50)
            )
            .padding(
                horizontal = 10.dp,
                vertical = 6.dp
            ),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = statusColor
        )
    }
}