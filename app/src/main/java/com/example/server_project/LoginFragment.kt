package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment
import com.example.server_project.R
import com.example.server_project.LoginFormFragment


class LoginFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_login, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val loginBtn = view.findViewById<Button>(R.id.btn_login)

        loginBtn.setOnClickListener {
            // LoginFormFragment로 화면 전환
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, LoginFormFragment())
                .addToBackStack(null)
                .commit()
        }
    }
}
