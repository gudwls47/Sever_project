package com.example.server_project.ui

import android.os.Bundle
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.example.server_project.StoreTabContentFragment

class StoreDetailPagerAdapter(
    fragment: Fragment,
    private val itemCount: Int,
    private val restaurantName: String // ✅ restaurantName 추가
) : FragmentStateAdapter(fragment) {

    override fun getItemCount(): Int = itemCount

    override fun createFragment(position: Int): Fragment {
        return StoreTabContentFragment.newInstance(position).apply {
            arguments = (arguments ?: Bundle()).apply {
                putString("restaurantName", restaurantName) // 함께 전달
            }
        }
    }
}