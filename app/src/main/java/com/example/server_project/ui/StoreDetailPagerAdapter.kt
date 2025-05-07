package com.example.server_project.ui

import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.example.server_project.StoreTabContentFragment

class StoreDetailPagerAdapter(
    fragment: Fragment,
    private val itemCount: Int
) : FragmentStateAdapter(fragment) {

    override fun getItemCount(): Int = itemCount

    override fun createFragment(position: Int): Fragment {
        return StoreTabContentFragment.newInstance(position)
    }
}
