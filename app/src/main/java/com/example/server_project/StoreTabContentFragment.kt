package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.ui.StoreReviewAdapter
import com.example.server_project.model.ReviewerReview

class StoreTabContentFragment : Fragment() {

    companion object {
        fun newInstance(tabIndex: Int): StoreTabContentFragment {
            val fragment = StoreTabContentFragment()
            val args = Bundle()
            args.putInt("tabIndex", tabIndex)
            fragment.arguments = args
            return fragment
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_store_tab_content, container, false)
        val tabIndex = arguments?.getInt("tabIndex") ?: 0
        val containerLayout = view.findViewById<LinearLayout>(R.id.tab_content_container)

        when (tabIndex) {
            0 -> {
                addText(containerLayout, "위치: 서울특별시 동작구 상도로 123")
                addText(containerLayout, "영업 중 / 오더 시간: 오전 11시 ~ 오후 9시")
                addText(containerLayout, "전화번호: 02-123-4567")
                addText(containerLayout, "인스타 및 블로그: @milal_kitchen")
                addText(containerLayout, "단체 이용 가능, 포장 예약, 무선 인터넷 제공")
            }
            1 -> addText(containerLayout, "소식 탭입니다. 이벤트나 공지사항 표시.")
            2 -> addText(containerLayout, "메뉴 탭입니다. 대표 메뉴 이미지나 설명.")
            3 -> {
                val reviewView = layoutInflater.inflate(R.layout.fragment_store_tab_review, containerLayout, false)

                val restaurantName = arguments?.getString("restaurantName") ?: "가게 이름"
                val prompt = reviewView.findViewById<TextView>(R.id.tv_review_prompt)
                prompt.text = "‘$restaurantName’을 다녀오셨나요?\n클립과 리뷰로 경험을 남겨보세요!"

                val dummyImages = listOf(
                    R.drawable.sample_food_image,
                    R.drawable.sample_food_image1
                )

                val dummyReviews = listOf(
                    ReviewerReview(restaurantName, 4.5f, "음식이 훌륭했어요!", dummyImages),
                    ReviewerReview(restaurantName, 4.0f, "분위기도 좋아요!", dummyImages),
                    ReviewerReview(restaurantName, 3.5f, "기대 이상은 아니에요", dummyImages),
                    ReviewerReview(restaurantName, 2.0f, "조금 아쉬웠어요", dummyImages),
                    ReviewerReview(restaurantName, 5.0f, "최고입니다!!", dummyImages)
                )

                val recyclerView = reviewView.findViewById<RecyclerView>(R.id.recycler_store_reviews)
                recyclerView.layoutManager = LinearLayoutManager(requireContext())
                recyclerView.adapter = StoreReviewAdapter(dummyReviews)

                val countText = reviewView.findViewById<TextView>(R.id.tv_review_count)
                countText.text = "리뷰 ${dummyReviews.size}"

                val reviewWriteButton = reviewView.findViewById<FrameLayout>(R.id.btn_review_write)
                reviewWriteButton.setOnClickListener {
                    requireActivity().supportFragmentManager.beginTransaction()
                        .replace(R.id.main_frm, ReviewWriteFragment())
                        .addToBackStack(null)
                        .commit()
                }

                containerLayout.addView(reviewView)
            }
            4 -> addText(containerLayout, "사진 탭입니다. 이용자 사진들 나열.")
            5 -> addText(containerLayout, "주변 탭입니다. 가까운 장소 정보.")
            6 -> addText(containerLayout, "정보 탭입니다. 사업자 정보 및 운영 정보.")
        }

        return view
    }

    private fun addText(layout: LinearLayout, text: String) {
        val textView = TextView(requireContext()).apply {
            this.text = text
            textSize = 17f
            setPadding(0, 10, 0, 8)
            setTextColor(android.graphics.Color.BLACK)
        }
        layout.addView(textView)
    }
}