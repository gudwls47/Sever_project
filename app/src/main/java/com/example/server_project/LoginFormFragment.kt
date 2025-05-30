package com.example.server_project

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.server_project.api.LoginRequest
import com.example.server_project.api.LoginResponse
import com.example.server_project.api.RetrofitInstance
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.util.Log

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
        val editId = view.findViewById<EditText>(R.id.edit_login_id)
        val editPassword = view.findViewById<EditText>(R.id.edit_login_password)
        val loginButton = view.findViewById<Button>(R.id.btn_loginform)

        backBtn.setOnClickListener {
            parentFragmentManager.popBackStack()
        }

        loginButton.setOnClickListener {
            val id = editId.text.toString().trim()
            val password = editPassword.text.toString().trim()

            if (id.isEmpty() || password.isEmpty()) {
                Toast.makeText(requireContext(), "아이디와 비밀번호를 모두 입력해주세요.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val loginRequest = LoginRequest(id, password)

            RetrofitInstance.api.loginUser(loginRequest).enqueue(object : Callback<LoginResponse> {
                override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                    if (response.isSuccessful && response.body() != null) {
                        val loginResponse = response.body()!!

                        Log.d("DEBUG_LOGIN", "로그인 응답 userId: ${loginResponse.userId}")

                        // ✅ user_id 저장
                        val sharedPref = requireActivity().getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
                        with(sharedPref.edit()) {
                            putInt("user_id", loginResponse.userId)
                            apply()
                        }

                        Toast.makeText(requireContext(), "로그인 성공", Toast.LENGTH_SHORT).show()

                        // ✅ HomeFragment로 이동
                        parentFragmentManager.beginTransaction()
                            .replace(R.id.main_frm, HomeFragment())
                            .addToBackStack(null)
                            .commit()
                    } else {
                        Toast.makeText(requireContext(), "로그인 실패: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    Toast.makeText(requireContext(), "로그인 오류: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }
}
