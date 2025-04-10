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
import com.example.server_project.LoginFragment

class SignupInfoFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_signup_info, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val backBtn = view.findViewById<View>(R.id.btn_back)
        backBtn.setOnClickListener {
            parentFragmentManager.popBackStack() // 이전 프래그먼트로 돌아가기
        }

        val editId = view.findViewById<EditText>(R.id.edit_id)
        val editPassword = view.findViewById<EditText>(R.id.edit_password)
        val editNickname = view.findViewById<EditText>(R.id.edit_nickname)
        val editPhone = view.findViewById<EditText>(R.id.edit_phone)
        val finishButton = view.findViewById<Button>(R.id.btn_finish_signup)

        finishButton.setOnClickListener {
            val id = editId.text.toString().trim()
            val password = editPassword.text.toString().trim()
            val nickname = editNickname.text.toString().trim()
            val phone = editPhone.text.toString().trim()

            if (id.isNotEmpty() && password.isNotEmpty() && nickname.isNotEmpty() && phone.isNotEmpty()) {
                parentFragmentManager.beginTransaction()
                    .replace(R.id.main_frm, LoginFragment())
                    .addToBackStack(null)
                    .commit()
            } else {
                Toast.makeText(requireContext(), "모든 정보를 입력해주세요.", Toast.LENGTH_SHORT).show()
            }
        }
    }

}
