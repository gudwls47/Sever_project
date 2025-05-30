package com.example.server_project

import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.bumptech.glide.Glide
import com.example.server_project.api.RetrofitInstance
import com.example.server_project.api.UserProfileResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MypageFragment : Fragment() {

    private var textNickname: TextView? = null
    private var imgProfile: ImageView? = null
    private var btnEditInfo: Button? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_mypage, container, false)

        textNickname = view.findViewById(R.id.text_nickname)
        imgProfile = view.findViewById(R.id.img_profile)
        btnEditInfo = view.findViewById(R.id.btn_edit_info)

        val sharedPref = requireActivity().getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
        val userId = sharedPref.getInt("user_id", 0)

        if (userId != 0) {
            loadUserProfile(userId)
        } else {
            Toast.makeText(requireContext(), "로그인 정보가 없습니다.", Toast.LENGTH_SHORT).show()
        }

        btnEditInfo?.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, EditProfileFragment())
                .addToBackStack(null)
                .commit()
        }

        return view
    }

    private fun loadUserProfile(userId: Int) {
        RetrofitInstance.api.getUserProfile(userId).enqueue(object : Callback<UserProfileResponse> {
            override fun onResponse(call: Call<UserProfileResponse>, response: Response<UserProfileResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val profile = response.body()!!
                    textNickname?.text = profile.nickname
                    if (!profile.profile_image.isNullOrEmpty()) {
                        Glide.with(this@MypageFragment)
                            .load(profile.profile_image)
                            .into(imgProfile!!)
                    } else {
                        imgProfile?.setImageResource(R.drawable.ic_profile_placeholder) // 기본 이미지
                    }
                } else {
                    Toast.makeText(requireContext(), "프로필 정보를 불러올 수 없습니다.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<UserProfileResponse>, t: Throwable) {
                Toast.makeText(requireContext(), "프로필 로드 실패: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    override fun onDestroyView() {
        super.onDestroyView()
        textNickname = null
        imgProfile = null
        btnEditInfo = null
    }
}
