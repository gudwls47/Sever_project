package com.example.server_project

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.bumptech.glide.Glide
import com.example.server_project.api.RetrofitInstance
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.util.Log
import com.example.server_project.api.UserProfileResponse

class EditProfileFragment : Fragment() {

    private lateinit var editNickname: EditText
    private lateinit var tvNickname: TextView
    private lateinit var btnEditNickname: ImageView
    private lateinit var btnCamera: ImageView
    private var userId: Int = 0

    private var selectedImageUri: Uri? = null

    // 권한 요청 결과 처리
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            openImageChooser() // 권한 허용되면 이미지 선택창 열기
        } else {
            Toast.makeText(requireContext(), "권한이 거부되어 이미지를 선택할 수 없습니다.", Toast.LENGTH_SHORT).show()
        }
    }

    // 이미지 선택 결과 처리
    private val getImage = registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        uri?.let {
            selectedImageUri = it
            val imgProfile = view?.findViewById<ImageView>(R.id.img_profile)
            imgProfile?.setImageURI(it)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_edit_profile, container, false)

        editNickname = view.findViewById(R.id.edit_nickname)
        tvNickname = view.findViewById(R.id.tv_nickname)
        btnEditNickname = view.findViewById(R.id.btn_edit_nickname)
        btnCamera = view.findViewById(R.id.btn_camera)
        val backButton = view.findViewById<ImageView>(R.id.btn_back)
        val saveButton = view.findViewById<TextView>(R.id.btn_save)
        val logoutButton = view.findViewById<Button>(R.id.btn_logout)
        val imgProfile = view.findViewById<ImageView>(R.id.img_profile)

        val sharedPref = requireActivity().getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
        userId = sharedPref.getInt("user_id", 0)

        if (userId > 0) {
            loadUserProfile(userId, imgProfile)
        } else {
            Toast.makeText(requireContext(), "로그인 정보가 없습니다.", Toast.LENGTH_SHORT).show()
        }

        backButton.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, MypageFragment())
                .commit()
        }

        btnEditNickname.setOnClickListener {
            tvNickname.visibility = View.GONE
            editNickname.visibility = View.VISIBLE
            editNickname.requestFocus()
            val imm = requireContext().getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
            imm.showSoftInput(editNickname, InputMethodManager.SHOW_IMPLICIT)
        }

        btnCamera.setOnClickListener {
            checkPermissionAndOpenChooser()
        }

        saveButton.setOnClickListener {
            val newNickname = editNickname.text.toString().trim()
            if (newNickname.isEmpty()) {
                Toast.makeText(requireContext(), "닉네임을 입력해주세요.", Toast.LENGTH_SHORT).show()
            } else {
                saveNickname(userId, newNickname)
                selectedImageUri?.let { uri ->
                    uploadProfileImage(userId, uri.toString()) // 서버에 맞게 변환 필요
                }
            }
        }

        logoutButton.setOnClickListener {
            Toast.makeText(requireContext(), "로그아웃 되었습니다.", Toast.LENGTH_SHORT).show()
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, LoginFormFragment())
                .commit()
        }

        return view
    }

    private fun checkPermissionAndOpenChooser() {
        val permission = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            Manifest.permission.READ_MEDIA_IMAGES
        } else {
            Manifest.permission.READ_EXTERNAL_STORAGE
        }

        when {
            ContextCompat.checkSelfPermission(requireContext(), permission) == PackageManager.PERMISSION_GRANTED -> {
                openImageChooser()
            }
            shouldShowRequestPermissionRationale(permission) -> {
                Toast.makeText(requireContext(), "이미지 선택을 위해 권한이 필요합니다.", Toast.LENGTH_SHORT).show()
                requestPermissionLauncher.launch(permission)
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun openImageChooser() {
        getImage.launch("image/*")
    }

    // 서버에서 닉네임과 프로필 이미지 같이 불러오기
    private fun loadUserProfile(userId: Int, imgProfile: ImageView) {
        RetrofitInstance.api.getUserProfile(userId).enqueue(object : Callback<UserProfileResponse> {
            override fun onResponse(call: Call<UserProfileResponse>, response: Response<UserProfileResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val profile = response.body()!!
                    editNickname.setText(profile.nickname)
                    tvNickname.text = profile.nickname
                    editNickname.visibility = View.GONE
                    tvNickname.visibility = View.VISIBLE

                    if (!profile.profile_image.isNullOrEmpty()) {
                        Glide.with(requireContext())
                            .load(profile.profile_image)
                            .placeholder(R.drawable.ic_profile_placeholder)
                            .into(imgProfile)
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

    private fun saveNickname(userId: Int, newNickname: String) {
        val requestBody = mapOf("nickname" to newNickname)
        Log.d("DEBUG_NICKNAME", "Request body: $requestBody")
        RetrofitInstance.api.updateUserNickname(userId, requestBody)
            .enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    if (response.isSuccessful) {
                        Toast.makeText(requireContext(), "닉네임이 변경되었습니다.", Toast.LENGTH_SHORT).show()
                        tvNickname.text = newNickname
                        editNickname.visibility = View.GONE
                        tvNickname.visibility = View.VISIBLE
                    } else {
                        Toast.makeText(requireContext(), "닉네임 변경 실패: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Toast.makeText(requireContext(), "닉네임 변경 오류: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    fun uploadProfileImage(userId: Int, imageUrl: String) {
        val requestBody = mapOf("profile_image_url" to imageUrl)
        RetrofitInstance.api.updateProfileImage(userId, requestBody)
            .enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    if (response.isSuccessful) {
                        Toast.makeText(context, "프로필 이미지가 변경되었습니다.", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, "이미지 변경 실패: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Toast.makeText(context, "이미지 변경 오류: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
