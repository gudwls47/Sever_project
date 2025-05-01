package com.example.server_project.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.model.Reviewer

class ReviewerAdapter(private val reviewerList: List<Reviewer>) :
    RecyclerView.Adapter<ReviewerAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imgProfile: ImageView = view.findViewById(R.id.img_reviewer)
        val tvRank: TextView = view.findViewById(R.id.tv_rank)
        val tvName: TextView = view.findViewById(R.id.tv_name)
        val tvTemperature: TextView = view.findViewById(R.id.tv_temperature_value)
        val tvEmoji: TextView = view.findViewById(R.id.tv_emoji)
        val progressBar: ProgressBar = view.findViewById(R.id.progress_temperature)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_reviewer, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val reviewer = reviewerList[position]

        holder.imgProfile.setImageResource(reviewer.profileImageRes)
        holder.tvRank.text = reviewer.rank
        holder.tvName.text = reviewer.name
        holder.tvTemperature.text = "${reviewer.temperature}도"
        holder.progressBar.progress = reviewer.temperature.toInt()

        holder.tvEmoji.text = when (reviewer.temperature) {
            in 90f..100f -> "😍"
            in 70f..89.9f -> "🙂"
            in 50f..69.9f -> "😐"
            else -> "☹️"
        }

        // ✅ 클릭 시 ReviewerFragment로 이동
        holder.itemView.findViewById<View>(R.id.btn_home_box).setOnClickListener {
            val fragment = ReviewerFragment().apply {
                arguments = Bundle().apply {
                    putString("name", reviewer.name)
                    putFloat("temperature", reviewer.temperature)
                    putInt("reviewCount", reviewer.temperature.toInt()) // 추후 수정 가능
                }
            }

            (it.context as AppCompatActivity).supportFragmentManager.beginTransaction()
                .replace(R.id.main_frm, fragment)
                .addToBackStack(null)
                .commit()
        }
    }

    override fun getItemCount(): Int = reviewerList.size
}
