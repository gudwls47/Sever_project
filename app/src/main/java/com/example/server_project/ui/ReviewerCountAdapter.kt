package com.example.server_project.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.model.Reviewer

class ReviewerCountAdapter(private val reviewerList: List<Reviewer>) :
    RecyclerView.Adapter<ReviewerCountAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imgProfile: ImageView = view.findViewById(R.id.img_reviewer)
        val tvRank: TextView = view.findViewById(R.id.tv_rank)
        val tvName: TextView = view.findViewById(R.id.tv_name)
        val tvReviewCount: TextView = view.findViewById(R.id.tv_review_count)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_reviewer_count, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val reviewer = reviewerList[position]
        holder.imgProfile.setImageResource(reviewer.profileImageRes)
        holder.tvRank.text = reviewer.rank
        holder.tvName.text = reviewer.name
        holder.tvReviewCount.text = " ${reviewer.temperature.toInt()} 개"
    }

    override fun getItemCount(): Int = reviewerList.size
}
