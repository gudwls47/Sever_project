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
        val imageRow1: LinearLayout = view.findViewById(R.id.layout_images_row1)
        val imageRow2: LinearLayout = view.findViewById(R.id.layout_images_row2)
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
        holder.imageRow1.removeAllViews()
        holder.imageRow2.removeAllViews()

        val images = review.imageList.take(4)

        images.take(2).forEach { resId ->
            val imageView = ImageView(holder.itemView.context).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(100, 100).apply {
                    setMargins(4, 4, 4, 4)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            holder.imageRow1.addView(imageView)
        }

        images.drop(2).forEach { resId ->
            val imageView = ImageView(holder.itemView.context).apply {
                setImageResource(resId)
                layoutParams = LinearLayout.LayoutParams(100, 100).apply {
                    setMargins(4, 4, 4, 4)
                }
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            holder.imageRow2.addView(imageView)
        }

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
