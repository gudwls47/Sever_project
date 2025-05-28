package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import com.example.server_project.R

class ReviewWriteFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_review, container, false)

        val ratingBar = view.findViewById<RatingBar>(R.id.rating_overall)
        val tasteGroup = view.findViewById<RadioGroup>(R.id.radio_taste)
        val priceGroup = view.findViewById<RadioGroup>(R.id.radio_price)
        val serviceGroup = view.findViewById<RadioGroup>(R.id.radio_service)
        val receiptImage = view.findViewById<ImageView>(R.id.img_receipt)
        val reviewEditText = view.findViewById<EditText>(R.id.et_review)
        val saveButton = view.findViewById<TextView>(R.id.btn_save)
        val backButton = view.findViewById<ImageView>(R.id.btn_back)

        // 뒤로가기 버튼 클릭 시
        backButton.setOnClickListener {
            parentFragmentManager.popBackStack()
        }

        // 저장 버튼 클릭 시
        saveButton.setOnClickListener {
            val overallRating = ratingBar.rating
            val tasteRating = getSelectedRating(tasteGroup)
            val priceRating = getSelectedRating(priceGroup)
            val serviceRating = getSelectedRating(serviceGroup)
            val reviewText = reviewEditText.text.toString()

            // TODO: 서버 전송 또는 로컬 저장 처리
            Toast.makeText(requireContext(), "리뷰가 저장되었습니다", Toast.LENGTH_SHORT).show()

            // 이전 화면으로 돌아가기
            parentFragmentManager.popBackStack()
        }

        // 영수증 이미지 클릭 시
        receiptImage.setOnClickListener {
            Toast.makeText(requireContext(), "이미지 업로드 기능은 아직 구현되지 않았습니다.", Toast.LENGTH_SHORT).show()
        }

        return view
    }

    private fun getSelectedRating(group: RadioGroup): Int {
        return when (group.checkedRadioButtonId) {
            -1 -> 0 // 아무것도 선택 안 된 경우
            else -> group.indexOfChild(group.findViewById(group.checkedRadioButtonId)) + 1
        }
    }
}
