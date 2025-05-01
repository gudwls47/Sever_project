package com.example.server_project.ui

import android.annotation.SuppressLint
import android.graphics.Typeface
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.model.ReviewerReview

class ReviewerFragment : Fragment() {

    @SuppressLint("SetTextI18n")
    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_reviewer, container, false)

        // ✅ 데이터 수신
        val name = arguments?.getString("name") ?: "이름 없음"
        val temperature = arguments?.getFloat("temperature") ?: 0f
        val reviewCount = arguments?.getInt("reviewCount") ?: 0

        val emoji = when (temperature) {
            in 90f..100f -> "😍"
            in 70f..89.9f -> "🙂"
            in 50f..69.9f -> "😐"
            else -> "☹️"
        }

        view.findViewById<TextView>(R.id.tv_reviewer_name).text = name
        view.findViewById<TextView>(R.id.tv_temperature).text = "${temperature}도 $emoji"
        view.findViewById<TextView>(R.id.tv_review_count).text = "리뷰 갯수 : ${reviewCount}개"

        // ✅ 더미 리뷰 생성 (갯수는 reviewCount와 일치)
        val dummyImages = listOf(
            R.drawable.sample_food_image,
            R.drawable.sample_food_image1,
            R.drawable.sample_food_image2,
            R.drawable.sample_food_image1
        )

        val reviewList = List(reviewCount) {
            ReviewerReview(
                restaurantName = "Item $it",
                rating = 4.0f,
                content = "이것은 더미 리뷰입니다.",
                imageList = dummyImages
            )
        }

        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_reviewer_reviews)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = ReviewerReviewAdapter(reviewList)

        // ✅ 뒤로가기 버튼
        view.findViewById<View>(R.id.btn_back)?.setOnClickListener {
            requireActivity().onBackPressedDispatcher.onBackPressed()
        }



        // ✅ 온도 스텝 처리
        val stepPairs = listOf(
            Triple(R.id.step_0, R.id.step_0_overlay, R.id.step_0_label),
            Triple(R.id.step_25, R.id.step_25_overlay, R.id.step_25_label),
            Triple(R.id.step_50, R.id.step_50_overlay, R.id.step_50_label),
            Triple(R.id.step_75, R.id.step_75_overlay, R.id.step_75_label),
            Triple(R.id.step_100, R.id.step_100_overlay, R.id.step_100_label)
        )

        val stepStates = mutableMapOf<Int, Boolean>()  // 선택 상태 저장용

        stepPairs.forEach { (frameId, overlayId, labelId) ->
            val frame = view.findViewById<View>(frameId)
            val overlay = view.findViewById<View>(overlayId)
            val label = view.findViewById<TextView>(labelId)

            stepStates[frameId] = false

            frame.setOnClickListener {
                val selected = stepStates[frameId] ?: false
                if (selected) {
                    overlay.visibility = View.INVISIBLE
                    label.setTypeface(null, Typeface.NORMAL)
                    stepStates[frameId] = false
                } else {
                    stepPairs.forEach { (fid, oid, lid) ->
                        view.findViewById<View>(oid).visibility = View.INVISIBLE
                        view.findViewById<TextView>(lid).setTypeface(null, Typeface.NORMAL)
                        stepStates[fid] = false
                    }
                    overlay.visibility = View.VISIBLE
                    label.setTypeface(null, Typeface.BOLD)
                    stepStates[frameId] = true
                }
            }
        }

        return view
    }
}
