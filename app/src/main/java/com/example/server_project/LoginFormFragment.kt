package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.server_project.R
import com.example.server_project.HomeFragment

class LoginFormFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_login_form, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val backBtn = view.findViewById<View>(R.id.btn_back)
        backBtn.setOnClickListener {
            parentFragmentManager.popBackStack()
        }

        val editId = view.findViewById<EditText>(R.id.edit_login_id)
        val editPassword = view.findViewById<EditText>(R.id.edit_login_password)
        val loginButton = view.findViewById<Button>(R.id.btn_loginform)

        loginButton.setOnClickListener {
            val id = editId.text.toString().trim()
            val password = editPassword.text.toString().trim()

            if (id.isNotEmpty() && password.isNotEmpty()) {
                parentFragmentManager.beginTransaction()
                    .replace(R.id.main_frm, HomeFragment())
                    .addToBackStack(null)
                    .commit()
            } else {
                Toast.makeText(requireContext(), "아이디와 비밀번호를 모두 입력해주세요.", Toast.LENGTH_SHORT).show()
            }
        }
    }

}
