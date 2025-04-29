package com.example.server_project.adapter

import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.example.server_project.ui.ReviewCountFragment
import com.example.server_project.ui.TemperatureFragment

class HomeTabAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {

    override fun getItemCount(): Int = 2

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> TemperatureFragment()
            1 -> ReviewCountFragment()
            else -> TemperatureFragment()
        }
    }
}
