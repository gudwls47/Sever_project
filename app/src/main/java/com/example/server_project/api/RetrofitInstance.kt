package com.example.server_project.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    val api: ServerApi by lazy {
        Retrofit.Builder()
            .baseUrl("http://10.0.2.2:5001/") // ← IP 주소 실제 서버에 맞게 설정
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ServerApi::class.java)
    }
}
