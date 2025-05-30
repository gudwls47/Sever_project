package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import kotlinx.coroutines.*
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.io.BufferedWriter
import java.io.OutputStreamWriter
import android.util.Log



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
        val editId = view.findViewById<EditText>(R.id.edit_id)
        val editPassword = view.findViewById<EditText>(R.id.edit_password)
        val editNickname = view.findViewById<EditText>(R.id.edit_nickname)
        val editPhone = view.findViewById<EditText>(R.id.edit_phone)
        val checkFemale = view.findViewById<CheckBox>(R.id.check_female)
        val checkMale = view.findViewById<CheckBox>(R.id.check_male)
        val finishButton = view.findViewById<Button>(R.id.btn_finish_signup)

        backBtn.setOnClickListener {
            parentFragmentManager.popBackStack() // 뒤로가기
        }

        // 성별 체크박스는 하나만 선택되게
        checkFemale.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) checkMale.isChecked = false
        }

        checkMale.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) checkFemale.isChecked = false
        }

        finishButton.setOnClickListener {
            val id = editId.text.toString().trim()
            val password = editPassword.text.toString().trim()
            val nickname = editNickname.text.toString().trim()
            val phone = editPhone.text.toString().trim()
            val gender = when {
                checkFemale.isChecked -> "여성"
                checkMale.isChecked -> "남성"
                else -> ""
            }

            if (id.isNotEmpty() && password.isNotEmpty() && nickname.isNotEmpty() && phone.isNotEmpty() && gender.isNotEmpty()) {
                signup(id, password, nickname, gender, phone)
            } else {
                Toast.makeText(requireContext(), "모든 정보를 입력해주세요.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun signup(id: String, password: String, nickname: String, gender: String, phone: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val json = JSONObject().apply {
                    put("username", id)
                    put("password_hash", password)
                    put("nickname", nickname)
                    put("gender", gender)
                    put("contact", phone)
                }

                Log.d("DEBUG_JSON", json.toString())

                val url = URL("http://192.168.219.105:5000/users/signup") // 🛑 Flask 서버 주소 확인
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                conn.doOutput = true

                val outputStream = conn.outputStream
                val writer = BufferedWriter(OutputStreamWriter(outputStream, "UTF-8"))
                writer.write(json.toString())
                writer.flush()
                writer.close()
                outputStream.close()

                val responseCode = conn.responseCode
                val responseText = conn.inputStream.bufferedReader().use { it.readText() }

                withContext(Dispatchers.Main) {
                    if (responseCode == 201) {
                        Toast.makeText(requireContext(), "회원가입 성공!", Toast.LENGTH_SHORT).show()
                        parentFragmentManager.beginTransaction()
                            .replace(R.id.main_frm, LoginFragment())
                            .addToBackStack(null)
                            .commit()
                    } else {
                        Toast.makeText(requireContext(), "회원가입 실패: $responseText", Toast.LENGTH_LONG).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(requireContext(), "에러 발생: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
