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
import com.example.server_project.ui.ReviewerAdapter

class TemperatureFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_temperature, container, false)

        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_temperature)
        recyclerView.layoutManager = LinearLayoutManager(context)

        val reviewers = List(10) {
            Reviewer(
                rank = "${it + 1}등",
                name = "상도동 풍자",
                temperature = (100 - it * 10).toFloat(),
                profileImageRes = R.drawable.img_sample_profile
            )
        }

        recyclerView.adapter = ReviewerAdapter(reviewers)
        return view
    }
}
