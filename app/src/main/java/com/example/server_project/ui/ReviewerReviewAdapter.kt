package com.example.server_project.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RatingBar
import android.widget.TextView
import androidx.fragment.app.FragmentActivity
import androidx.recyclerview.widget.RecyclerView
import com.example.server_project.R
import com.example.server_project.ReviewDetailFragment
import com.example.server_project.model.ReviewerReview

class ReviewerReviewAdapter(
    private val reviewList: List<ReviewerReview>
) : RecyclerView.Adapter<ReviewerReviewAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val restaurantName: TextView = view.findViewById(R.id.tv_restaurant_name)
        val ratingBar: RatingBar = view.findViewById(R.id.rating_bar)
        val content: TextView = view.findViewById(R.id.tv_review_content)
        val imageLayout: LinearLayout = view.findViewById(R.id.layout_images)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_reviewer_review, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val review = reviewList[position]
        holder.restaurantName.text = review.restaurantName
        holder.ratingBar.rating = review.rating
        holder.content.text = review.content

        // 이미지 초기화 (재활용 대응)
        holder.imageLayout.removeAllViews()

        review.imageList.take(4).forEach { resId ->
            val imageView = ImageView(holder.itemView.context).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(100, 100).apply {
                    setMargins(8, 0, 8, 0)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            holder.imageLayout.addView(imageView)
        }

        // ✅ 아이템 클릭 → 상세 페이지로 이동
        holder.itemView.setOnClickListener {
            val context = holder.itemView.context
            val activity = context as? FragmentActivity ?: return@setOnClickListener

            val bundle = Bundle().apply {
                putString("restaurantName", review.restaurantName)
                putFloat("rating", review.rating)
                putString("reviewText", review.content)
                putIntegerArrayList("imageList", ArrayList(review.imageList))
            }

            val fragment = ReviewDetailFragment().apply {
                arguments = bundle
            }

            activity.supportFragmentManager.beginTransaction()
                .replace(R.id.main_frm, fragment)
                .addToBackStack(null)
                .commit()
        }
    }

    override fun getItemCount(): Int = reviewList.size
}
