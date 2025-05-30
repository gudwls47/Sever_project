package com.example.server_project.api

data class UserProfileResponse(
    val nickname: String,
    val profile_image: String?  // 이미지 URL, null일 수도 있으니 nullable로
)