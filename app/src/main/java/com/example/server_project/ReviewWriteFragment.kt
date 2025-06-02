package com.example.server_project

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import com.example.server_project.api.*
import com.example.server_project.util.FileUtil
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.InputStream
import android.provider.OpenableColumns


class ReviewWriteFragment : Fragment() {

    private var userId: Int = 0
    private var restaurantId: Int = 0
    private var selectedImageUri: Uri? = null

    private lateinit var receiptImage: ImageView
    private lateinit var imagePickerLauncher: ActivityResultLauncher<Intent>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        imagePickerLauncher = registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                selectedImageUri = result.data?.data
                receiptImage.setImageURI(selectedImageUri)
            }
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_review, container, false)

        val ratingBar = view.findViewById<RatingBar>(R.id.rating_overall)
        val tasteGroup = view.findViewById<RadioGroup>(R.id.radio_taste)
        val priceGroup = view.findViewById<RadioGroup>(R.id.radio_price)
        val serviceGroup = view.findViewById<RadioGroup>(R.id.radio_service)
        val reviewEditText = view.findViewById<EditText>(R.id.et_review)
        val saveButton = view.findViewById<TextView>(R.id.btn_save)
        val backButton = view.findViewById<ImageView>(R.id.btn_back)
        receiptImage = view.findViewById(R.id.img_receipt)

        val sharedPref = requireActivity().getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
        userId = sharedPref.getInt("user_id", 0)
        restaurantId = arguments?.getInt("restaurant_id") ?: DEFAULT_TEST_RESTAURANT_ID

        backButton.setOnClickListener {
            parentFragmentManager.popBackStack()
        }

        saveButton.setOnClickListener {
            val overallRating = ratingBar.rating.toInt()
            val tasteRating = getSelectedRating(tasteGroup)
            val priceRating = getSelectedRating(priceGroup)
            val serviceRating = getSelectedRating(serviceGroup)
            val reviewText = reviewEditText.text.toString()

            if (userId == 0 || restaurantId == 0 || reviewText.isEmpty()) {
                Toast.makeText(requireContext(), "입력값을 확인해주세요.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val reviewData = mapOf(
                "user_id" to userId,
                "restaurant_id" to restaurantId,
                "rating" to overallRating,
                "content" to reviewText,
                "receipt_verified" to false,
                "taste_rating" to tasteRating,
                "price_rating" to priceRating,
                "service_rating" to serviceRating
            )

            RetrofitInstance.api.createReview(reviewData).enqueue(object : Callback<Map<String, Any>> {
                override fun onResponse(call: Call<Map<String, Any>>, response: Response<Map<String, Any>>) {
                    if (!isAdded) return

                    if (response.isSuccessful) {
                        val reviewId = (response.body()?.get("review_id") as? Number)?.toInt() ?: 0
                        if (reviewId == 0) {
                            Toast.makeText(requireContext(), "리뷰 ID가 유효하지 않습니다.", Toast.LENGTH_SHORT).show()
                            return
                        }

                        if (selectedImageUri != null) {
                            val inputStream = requireContext().contentResolver.openInputStream(selectedImageUri!!)
                            val requestBody = inputStream!!.readBytes().toRequestBody("image/*".toMediaTypeOrNull())
                            val fileName = getFileNameFromUri(requireContext(), selectedImageUri!!) ?: "upload.jpg"
                            val part = MultipartBody.Part.createFormData("file", fileName, requestBody)

                            RetrofitInstance.api.uploadReviewImage(part).enqueue(object : Callback<Map<String, String>> {
                                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                                    val imageUrl = response.body()?.get("url") ?: ""
                                    if (imageUrl.isBlank()) {
                                        Toast.makeText(requireContext(), "이미지 업로드 실패", Toast.LENGTH_SHORT).show()
                                        return
                                    }

                                    val request = ReviewImageRequest(reviewId, imageUrl)
                                    RetrofitInstance.api.addReviewImage(request).enqueue(object : Callback<ApiResponse> {
                                        override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                                            Toast.makeText(requireContext(), "리뷰와 이미지가 등록되었습니다.", Toast.LENGTH_SHORT).show()
                                            parentFragmentManager.popBackStack()
                                        }

                                        override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                                            Toast.makeText(requireContext(), "이미지 저장 실패: ${t.message}", Toast.LENGTH_SHORT).show()
                                        }
                                    })
                                }

                                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                                    Toast.makeText(requireContext(), "이미지 업로드 실패: ${t.message}", Toast.LENGTH_SHORT).show()
                                }
                            })
                        } else {
                            Toast.makeText(requireContext(), "리뷰가 등록되었습니다.", Toast.LENGTH_SHORT).show()
                            parentFragmentManager.popBackStack()
                        }
                    } else {
                        Toast.makeText(requireContext(), "리뷰 등록 실패: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                    if (!isAdded) return
                    Toast.makeText(requireContext(), "서버 오류: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }

        receiptImage.setOnClickListener {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            imagePickerLauncher.launch(intent)
        }

        return view
    }

    private fun getSelectedRating(group: RadioGroup): Int {
        return when (group.checkedRadioButtonId) {
            -1 -> 0
            else -> group.indexOfChild(group.findViewById(group.checkedRadioButtonId)) + 1
        }
    }fun getFileNameFromUri(context: Context, uri: Uri): String? {
        var result: String? = null
        if (uri.scheme == "content") {
            val cursor = context.contentResolver.query(uri, null, null, null, null)
            cursor?.use {
                if (it.moveToFirst()) {
                    val index = it.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (index >= 0) result = it.getString(index)
                }
            }
        }
        if (result == null) {
            result = uri.path
            val cut = result?.lastIndexOf('/')
            if (cut != null && cut != -1) {
                result = result?.substring(cut + 1)
            }
        }
        return result
    }


    companion object {
        private const val DEFAULT_TEST_RESTAURANT_ID = 1
    }
}
