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

        val imageList = listOf(
            R.drawable.sample_food_image,
            R.drawable.sample_food_image1,
            R.drawable.sample_food_image2,
            R.drawable.sample_food_image3
        )

        val reviewList = listOf(
            ReviewerReview("핵밥", 4.5f, "밥이 고슬고슬하고 반찬도 하나하나 정성이 느껴졌어요. 다음에도 꼭 다시 방문할 예정입니다.", imageList),
            ReviewerReview("밀알 식당", 4.0f, "가격 대비 훌륭한 구성입니다. 특히 고등어조림이 깊은 맛이 나서 밥도둑이에요.", imageList),
            ReviewerReview("내찜닭", 4.8f, "찜닭 양도 많고 당면이 탱탱해서 만족스러웠어요. 매콤달콤한 맛이 딱 제 취향입니다.", imageList),
            ReviewerReview("서브웨이", 3.5f, "빵이 살짝 눅눅했지만 야채는 신선했고 빠르게 식사하기에 나쁘지 않았습니다.", imageList),
            ReviewerReview("롯데리아", 3.8f, "기대보단 나쁘지 않았어요. 불고기버거는 단맛이 강했지만 전 괜찮았어요.", imageList),
            ReviewerReview("맥도날드", 4.2f, "감튀가 아주 바삭했고 매장도 깔끔했어요. 셀프 키오스크로 주문도 편했어요.", imageList),
            ReviewerReview("KFC", 4.7f, "치킨은 역시 KFC답게 바삭하고 육즙 가득했습니다. 양도 푸짐했어요.", imageList),
            ReviewerReview("면식당", 3.9f, "국물 맛이 깊고 면발도 쫄깃했습니다. 기본에 충실한 한 끼였어요.", imageList),
            ReviewerReview("은하수", 4.6f, "조용한 분위기에서 식사할 수 있어서 좋았고 음식도 담백하고 건강한 느낌이었어요.", imageList),
            ReviewerReview("청년다방", 4.3f, "로제 떡볶이가 부드럽고 매콤했어요. 튀김도 고소하고 바삭해서 완벽한 조합!", imageList)
        )


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
