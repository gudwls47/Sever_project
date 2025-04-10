package com.example.server_project

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.server_project.R

class SignupAgreementFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_signup_agreement, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // 체크박스 및 버튼 참조
        val checkAll = view.findViewById<CheckBox>(R.id.check_all)
        val checkAge = view.findViewById<CheckBox>(R.id.check_age)
        val checkTerms = view.findViewById<CheckBox>(R.id.check_terms)
        val checkCollect = view.findViewById<CheckBox>(R.id.check_collect)
        val checkPolicy = view.findViewById<CheckBox>(R.id.check_policy)
        val checkThirdParty = view.findViewById<CheckBox>(R.id.check_third_party)
        val checkMarketing = view.findViewById<CheckBox>(R.id.check_marketing)
        val nextButton = view.findViewById<Button>(R.id.btn_next)

        // 필수 항목만 따로 리스트로 관리
        val requiredCheckboxes = listOf(
            checkAge, checkTerms, checkCollect,
            checkPolicy, checkThirdParty
        )

        // 전체 항목(선택 포함) 리스트 (선택적으로 사용 가능)
        val allCheckboxes = requiredCheckboxes + checkMarketing

        // 전체 동의 누르면 → 모든 항목 체크
        checkAll.setOnCheckedChangeListener { _, isChecked ->
            allCheckboxes.forEach { it.isChecked = isChecked }
        }

        // 필수 항목들 중 하나라도 해제되면 전체동의도 해제
        requiredCheckboxes.forEach { checkbox ->
            checkbox.setOnCheckedChangeListener { _, _ ->
                checkAll.isChecked = requiredCheckboxes.all { it.isChecked }
            }
        }

        // 선택 항목 클릭 시에는 전체 동의 상태 변경 안 함
        checkMarketing.setOnCheckedChangeListener { _, _ ->
            // 아무 처리 안 함 (전체 동의 상태 영향 X)
        }

        // 다음 버튼 눌렀을 때 필수 항목 모두 선택되었는지 확인
        nextButton.setOnClickListener {
            val allRequiredChecked = requiredCheckboxes.all { it.isChecked }

            if (allRequiredChecked) {
                // 다음 화면(회원가입 정보 입력)으로 이동
                parentFragmentManager.beginTransaction()
                    .replace(R.id.main_frm, SignupInfoFragment())
                    .addToBackStack(null)
                    .commit()
            } else {
                // 필수 항목 미체크 시 경고
                Toast.makeText(requireContext(), "필수 항목을 모두 선택해주세요.", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
