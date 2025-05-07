package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RatingBar
import android.widget.TextView
import androidx.fragment.app.Fragment

class ReviewDetailFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_review_detail, container, false)

        // 전달받은 값
        val restaurantName = arguments?.getString("restaurantName") ?: "알 수 없음"
        val rating = arguments?.getFloat("rating") ?: 0f
        val reviewText = arguments?.getString("reviewText") ?: ""
        val imageResIds = arguments?.getIntegerArrayList("imageList") ?: arrayListOf()

        // 가게 이름 및 별점 세팅
        view.findViewById<TextView>(R.id.tv_store_name).text = restaurantName
        view.findViewById<RatingBar>(R.id.rating_bar).rating = rating
        view.findViewById<TextView>(R.id.tv_review_text).text = reviewText

        // 대표 이미지 세팅 (고정 이미지)
        val storeImages = listOf(
            R.drawable.img_store_sample1,
            R.drawable.img_store_sample2,
            R.drawable.img_store_sample3
        )

        val storeImageLayout = view.findViewById<LinearLayout>(R.id.layout_store_images)
        storeImages.forEach { resId ->
            val imageView = ImageView(requireContext()).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(0, 250, 1f).apply {
                    setMargins(8, 8, 8, 8)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            storeImageLayout.addView(imageView)
        }

        // 리뷰어가 찍은 사진 세팅
        val userImageLayout = view.findViewById<LinearLayout>(R.id.layout_user_images)
        imageResIds.forEach { resId ->
            val imageView = ImageView(requireContext()).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(0, 250, 1f).apply {
                    setMargins(8, 8, 8, 8)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            userImageLayout.addView(imageView)
        }

        // ✅ 뒤로가기 버튼 처리
        view.findViewById<ImageView>(R.id.btn_back)?.setOnClickListener {
            requireActivity().supportFragmentManager.popBackStack()
        }

        // ✅ 가게 정보 박스를 눌렀을 때 → StoreDetailFragment 로 이동
        val storeBox = view.findViewById<LinearLayout>(R.id.store_information_box)
        storeBox.setOnClickListener {
            val fragment = StoreDetailFragment().apply {
                arguments = Bundle().apply {
                    putString("restaurantName", restaurantName)
                    putFloat("rating", rating)
                    putIntegerArrayList("storeImages", ArrayList(storeImages)) // 전달
                }
            }

            requireActivity().supportFragmentManager.beginTransaction()
                .replace(R.id.main_frm, fragment)
                .addToBackStack(null)
                .commit()
        }

        return view
    }
}
