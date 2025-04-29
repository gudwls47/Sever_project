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

        val reviewers = List(10) {
            Reviewer(
                rank = "${it + 1}등",
                name = "상도동 풍자",
                temperature = (321 - it * 30).toFloat(), // 리뷰 수로 사용
                profileImageRes = R.drawable.img_sample_profile
            )
        }


        recyclerView.adapter = ReviewerCountAdapter(reviewers)
        return view
    }
}
