package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment
import com.example.server_project.R

class RankingStartFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_ranking_start, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val signupBtn = view.findViewById<Button>(R.id.btn_signup)

        signupBtn.setOnClickListener {
            // 회원가입 약관 화면으로 이동
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, SignupAgreementFragment())
                .addToBackStack(null)
                .commit()
        }
    }
}
