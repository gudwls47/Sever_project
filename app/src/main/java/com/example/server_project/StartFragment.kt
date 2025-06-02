package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment

class StartFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_start, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val signupButton = view.findViewById<Button>(R.id.btn_go_signup)
        val loginButton = view.findViewById<Button>(R.id.btn_go_login)

        signupButton.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, SignupAgreementFragment())
                .addToBackStack(null)
                .commit()
        }

        loginButton.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, LoginFormFragment())
                .addToBackStack(null)
                .commit()
        }
    }
}
