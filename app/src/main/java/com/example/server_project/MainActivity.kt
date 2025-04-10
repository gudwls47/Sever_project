package com.example.server_project

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.example.server_project.*

class MainActivity : AppCompatActivity() {

    private lateinit var bottomNav: BottomNavigationView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        bottomNav = findViewById(R.id.main_bnv)

        // 초기 프래그먼트 설정
        changeFragment(RankingStartFragment())

        bottomNav.setOnItemSelectedListener { item ->
            val fragment = when (item.itemId) {
                R.id.page_home -> HomeFragment()
                R.id.page_search -> SearchFragment()
                R.id.page_avatar -> AlarmFragment()
                R.id.page_mypage -> MypageFragment()
                else -> HomeFragment()
            }

            changeFragment(fragment)
            true
        }

        // 백스택 변화 감지해서 하단바 표시 갱신
        supportFragmentManager.addOnBackStackChangedListener {
            updateBottomNavVisibility()
        }
    }

    // 프래그먼트 전환 & 하단바 업데이트
    private fun changeFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.main_frm, fragment)
            .addToBackStack(null)
            .commit()

        updateBottomNavVisibility(fragment)
    }

    // 하단바 표시 여부 판단
    private fun updateBottomNavVisibility(fragment: Fragment? = null) {
        val currentFragment = fragment ?: supportFragmentManager.findFragmentById(R.id.main_frm)
        val hideBottomNavFragments = listOf(
            "RankingStartFragment",
            "LoginFormFragment",
            "LoginFragment",
            "SignupAgreementFragment",
            "SignupInfoFragment"
        )

        if (currentFragment != null &&
            hideBottomNavFragments.contains(currentFragment::class.java.simpleName)
        ) {
            bottomNav.visibility = View.GONE
        } else {
            bottomNav.visibility = View.VISIBLE
        }
    }
}
