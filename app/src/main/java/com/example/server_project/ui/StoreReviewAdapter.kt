package com.example.server_project.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RatingBar
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.model.ReviewerReview

class StoreReviewAdapter(private val reviews: List<ReviewerReview>) :
    RecyclerView.Adapter<StoreReviewAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val nickname: TextView = view.findViewById(R.id.tv_nickname)
        val content: TextView = view.findViewById(R.id.tv_review_text)
        val ratingBar: RatingBar = view.findViewById(R.id.rating_bar)
        val layoutImages: LinearLayout = view.findViewById(R.id.layout_images)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_store_review, parent, false)  // ✅ 새 레이아웃 사용
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = reviews.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = reviews[position]
        holder.nickname.text = "닉네임"  // 현재는 고정, 나중에 서버 연동 시 실제 닉네임 사용 가능
        holder.content.text = item.content
        holder.ratingBar.rating = item.rating

        holder.layoutImages.removeAllViews()
        item.imageList.take(4).forEach { resId ->
            val imageView = ImageView(holder.itemView.context).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(100, 100).apply {
                    setMargins(3, 0, 3, 0)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            holder.layoutImages.addView(imageView)
        }
    }
}