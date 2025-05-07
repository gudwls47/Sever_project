package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment

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
            0 -> { // 홈 탭
                addText(containerLayout, "위치: 서울특별시 동작구 상도로 123")
                addText(containerLayout, "영업 중 / 오더 시간: 오전 11시 ~ 오후 9시")
                addText(containerLayout, "전화번호: 02-123-4567")
                addText(containerLayout, "인스타 및 블로그: @milal_kitchen")
                addText(containerLayout, "단체 이용 가능, 포장 예약, 무선 인터넷 제공")
            }
            1 -> addText(containerLayout, "소식 탭입니다. 이벤트나 공지사항 표시.")
            2 -> addText(containerLayout, "메뉴 탭입니다. 대표 메뉴 이미지나 설명.")
            3 -> addText(containerLayout, "리뷰 탭입니다. 별점 및 한줄평 표시.")
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
