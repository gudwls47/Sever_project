// SignupRequest.kt
package com.example.server_project.api

data class SignupRequest(
    val username: String,
    val password_hash: String,
    val nickname: String,
    val gender: String,
    val contact: String
)
