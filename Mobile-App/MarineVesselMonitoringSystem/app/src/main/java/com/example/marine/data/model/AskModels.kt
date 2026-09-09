package com.example.marine.data.model

data class AskRequest(
    val question: String
)

data class AskResponse(
    val question: String? = null,
    val analysis: Any? = null,
    val rootCauses: List<String> = emptyList(),
    val report: String? = null,
)