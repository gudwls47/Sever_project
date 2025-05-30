package com.example.server_project.api
import com.google.gson.annotations.SerializedName

data class LoginResponse(
    val message: String,
    @SerializedName("user_id")
    val userId: Int
)

