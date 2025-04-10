package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment

class EditProfileFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_edit_profile, container, false)

        // 뒤로가기 버튼
        val backButton = view.findViewById<ImageView>(R.id.btn_back)
        backButton.setOnClickListener {
            // MypageFragment로 전환
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, MypageFragment())
                .commit()
        }

        // 저장 버튼 → 마이페이지 이동
        val saveButton = view.findViewById<TextView>(R.id.btn_save)
        saveButton.setOnClickListener {
            Toast.makeText(requireContext(), "정보가 저장되었습니다!", Toast.LENGTH_SHORT).show()

            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, MypageFragment())
                .commit()
        }

        // 로그아웃 버튼
        val logoutButton = view.findViewById<Button>(R.id.btn_logout)
        logoutButton.setOnClickListener {
            Toast.makeText(requireContext(), "로그아웃 되었습니다.", Toast.LENGTH_SHORT).show()

            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, LoginFragment())
                .commit()
        }

        return view
    }
}
