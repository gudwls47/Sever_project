// UserInfoResponse.kt
package com.example.server_project.api

data class UserInfoResponse(
    val user_id: Int,
    val username: String,
    val email: String?,
    val profile_image_url: String?,
    val trust_score: Int?,
    val activity_score: Int?
)
