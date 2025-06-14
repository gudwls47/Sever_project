package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import androidx.fragment.app.Fragment
import androidx.viewpager2.widget.ViewPager2
import com.example.server_project.ui.StoreDetailPagerAdapter
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator

class StoreDetailFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_store_detail, container, false)

        // ✅ 가게 이름 전달 (추후 arguments로 받을 수도 있음)
        val restaurantName = "핵밥" // 또는 arguments?.getString("restaurantName") ?: "알 수 없음"

        // ✅ 대표 이미지 추가
        val storeImages = listOf(
            R.drawable.img_store_sample1,
            R.drawable.img_store_sample2,
            R.drawable.img_store_sample3
        )

        val imageLayout = view.findViewById<LinearLayout>(R.id.layout_store_images)
        storeImages.forEach { resId ->
            val imageView = ImageView(requireContext()).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(0, 450, 1f).apply {
                    setMargins(3, 0, 3, 0)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            imageLayout.addView(imageView)
        }

        // ✅ 탭 + 뷰페이저 설정
        val tabTitles = listOf("홈", "소식", "메뉴", "리뷰", "사진", "주변", "정보")
        val viewPager = view.findViewById<ViewPager2>(R.id.view_pager_store)
        val tabLayout = view.findViewById<TabLayout>(R.id.tab_store)

        viewPager.adapter = StoreDetailPagerAdapter(this, tabTitles.size, restaurantName)

        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = tabTitles[position]
        }.attach()

        // ✅ 뒤로가기 버튼
        view.findViewById<ImageView>(R.id.btn_back).setOnClickListener {
            requireActivity().supportFragmentManager.popBackStack()
        }

        return view
    }
}