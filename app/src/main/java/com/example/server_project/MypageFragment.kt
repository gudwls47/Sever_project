package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment

class MypageFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_mypage, container, false)

        val editInfoButton = view.findViewById<Button>(R.id.btn_edit_info)
        editInfoButton.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, EditProfileFragment())
                .addToBackStack(null)
                .commit()
        }

        return view
    }
}