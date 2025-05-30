package com.example.server_project.api

import com.example.server_project.api.UploadResponse
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.PUT
import retrofit2.http.Headers
import retrofit2.http.Multipart
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Part
interface ServerApi {

    @POST("/users/login")
    fun loginUser(@Body request: LoginRequest): Call<LoginResponse>

    @POST("/users/signup")
    fun signupUser(@Body request: SignupRequest): Call<SignupResponse>

    @GET("/users/{user_id}/nickname")
    fun getUserNickname(@Path("user_id") userId: Int): Call<NicknameResponse>

    @Headers("Content-Type: application/json")
    @PUT("/users/{user_id}/nickname")
    fun updateUserNickname(
        @Path("user_id") userId: Int,
        @Body body: Map<String, String>
    ): Call<Void>

    @Headers("Content-Type: application/json")
    @PUT("/users/{user_id}/profile-image")
    fun updateProfileImage(
        @Path("user_id") userId: Int,
        @Body body: Map<String, String>
    ): Call<Void>

    @Multipart
    @POST("/upload/profile-image")
    fun uploadProfileImage(
        @Part file: MultipartBody.Part
    ): Call<UploadResponse>

    @GET("/users/{user_id}/profile")
    fun getUserProfile(@Path("user_id") userId: Int): Call<UserProfileResponse>

}
