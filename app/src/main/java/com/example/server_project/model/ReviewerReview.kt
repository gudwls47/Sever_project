package com.example.server_project.model

data class ReviewerReview(
    val restaurantName: String,
    val rating: Float,
    val content: String,
    val imageList: List<Int> // drawable 리소스 ID
)
