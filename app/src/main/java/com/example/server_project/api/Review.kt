package com.example.server_project.api

data class Review(
    val review_id: Int,
    val user_id: Int,
    val restaurant_id: Int,
    val rating: Int,
    val content: String,
    val restaurant_name: String,         // 식당 이름
    val nickname: String,                // 작성자 닉네임
    val profile_image: String?,          // 작성자 프로필 이미지 URL
    val taste_rating: Int?,              // 맛 점수
    val price_rating: Int?,              // 가격 점수
    val service_rating: Int?,            // 응대 점수
    val images: List<String>?            // 이미지 목록
)


