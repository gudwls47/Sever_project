package com.example.server_project.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.model.Reviewer

class ReviewCountFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_reviewcount, container, false)

        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_reviewcount)
        recyclerView.layoutManager = LinearLayoutManager(context)

        val names = listOf("상도동 풍자", "먹잘알", "냠냠", "먹짱", "서현", "형진", "우석", "용하", "8조최고", "맛있다")
            .shuffled() // ✅ 랜덤 순서로 섞기

        val reviewers = names.mapIndexed { index, name ->
            Reviewer(
                rank = "${index + 1}등",
                name = name,
                temperature = (321 - index * 30).toFloat(), // 리뷰 수로 활용
                profileImageRes = R.drawable.img_sample_profile
            )
        }


        recyclerView.adapter = ReviewerCountAdapter(reviewers)
        return view
    }
}
