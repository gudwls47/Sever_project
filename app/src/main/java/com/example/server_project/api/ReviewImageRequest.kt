package com.example.server_project.api

data class ReviewImageRequest(
    val review_id: Int,
    val image_url: String
)