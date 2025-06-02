package com.example.server_project

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.server_project.api.Review
import com.example.server_project.api.RetrofitInstance
import com.example.server_project.api.UserProfileResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.graphics.drawable.Drawable
import android.net.Uri
import com.bumptech.glide.load.DataSource
import com.bumptech.glide.load.engine.GlideException
import com.bumptech.glide.request.RequestListener
import com.bumptech.glide.request.target.Target

class MypageFragment : Fragment() {

    private var textNickname: TextView? = null
    private var imgProfile: ImageView? = null
    private var btnEditInfo: Button? = null
    private var recyclerView: RecyclerView? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_mypage, container, false)

        textNickname = view.findViewById(R.id.text_nickname)
        imgProfile = view.findViewById(R.id.img_profile)
        btnEditInfo = view.findViewById(R.id.btn_edit_info)
        recyclerView = view.findViewById(R.id.recycler_reviews)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        val sharedPref = requireActivity().getSharedPreferences("MyAppPrefs", Context.MODE_PRIVATE)
        val userId = sharedPref.getInt("user_id", 0)

        if (userId != 0) {
            loadUserProfile(userId)
            loadUserReviews(userId)
        } else {
            Toast.makeText(requireContext(), "로그인 정보가 없습니다.", Toast.LENGTH_SHORT).show()
        }

        btnEditInfo?.setOnClickListener {
            parentFragmentManager.beginTransaction()
                .replace(R.id.main_frm, EditProfileFragment())
                .addToBackStack(null)
                .commit()
        }

        return view
    }

    private fun loadUserProfile(userId: Int) {
        RetrofitInstance.api.getUserProfile(userId).enqueue(object : Callback<UserProfileResponse> {
            override fun onResponse(call: Call<UserProfileResponse>, response: Response<UserProfileResponse>) {
                if (response.isSuccessful && response.body() != null) {
                    val profile = response.body()!!
                    textNickname?.text = profile.nickname
                    if (!profile.profile_image.isNullOrEmpty()) {
                        Glide.with(this@MypageFragment)
                            .load(profile.profile_image)
                            .into(imgProfile!!)
                    } else {
                        imgProfile?.setImageResource(R.drawable.ic_profile_placeholder)
                    }
                } else {
                    Toast.makeText(requireContext(), "프로필 정보를 불러올 수 없습니다.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<UserProfileResponse>, t: Throwable) {
                Toast.makeText(requireContext(), "프로필 로드 실패: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun loadUserReviews(userId: Int) {
        RetrofitInstance.api.getUserReviews(userId).enqueue(object : Callback<List<Review>> {
            override fun onResponse(call: Call<List<Review>>, response: Response<List<Review>>) {
                if (response.isSuccessful && response.body() != null) {
                    val reviews = response.body()!!
                    reviews.forEach { review ->
                        Log.d("ReviewImageURL", "Review ID: ${review.review_id}, Image URLs: ${review.images}")
                    }
                    recyclerView?.adapter = ReviewAdapter(reviews)
                } else {
                    Toast.makeText(requireContext(), "리뷰 불러오기 실패", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Review>>, t: Throwable) {
                Toast.makeText(requireContext(), "리뷰 로드 실패: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    override fun onDestroyView() {
        super.onDestroyView()
        textNickname = null
        imgProfile = null
        btnEditInfo = null
        recyclerView = null
    }

    class ReviewAdapter(private val reviews: List<Review>) : RecyclerView.Adapter<ReviewAdapter.ViewHolder>() {
        inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val image: ImageView = view.findViewById(R.id.review_image)
            val restaurantName: TextView = view.findViewById(R.id.review_restaurant)
            val content: TextView = view.findViewById(R.id.review_content)
            val rating: RatingBar = view.findViewById(R.id.review_rating)
            val userId: TextView = view.findViewById(R.id.review_user_id)
            val userProfile: ImageView = view.findViewById(R.id.review_user_profile)
            val detailSummary: TextView = view.findViewById(R.id.review_detail_summary)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_review, parent, false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val review = reviews[position]
            holder.restaurantName.text = review.restaurant_name
            holder.content.text = review.content
            holder.rating.rating = review.rating.toFloat()
            holder.userId.text = review.nickname ?: "익명"
            holder.detailSummary.text = "맛: ${review.taste_rating} | 가격: ${review.price_rating} | 응대: ${review.service_rating}"

            if (!review.images.isNullOrEmpty()) {
                holder.image.visibility = View.VISIBLE
                val imageUrl = review.images[0].trim()
                Log.d("GlideLoad", "Loading image: $imageUrl")

                Glide.with(holder.itemView.context)
                    .load(Uri.parse(imageUrl))
                    .listener(object : RequestListener<Drawable> {
                        override fun onLoadFailed(
                            e: GlideException?, model: Any?, target: Target<Drawable>?, isFirstResource: Boolean
                        ): Boolean {
                            Log.e("GlideError", "Image load failed: $imageUrl", e)
                            return false // false로 해야 기본 에러 처리도 진행됨
                        }

                        override fun onResourceReady(
                            resource: Drawable?, model: Any?, target: Target<Drawable>?, dataSource: DataSource?, isFirstResource: Boolean
                        ): Boolean {
                            Log.d("GlideSuccess", "Image loaded successfully: $imageUrl")
                            return false
                        }
                    })
                    .into(holder.image)
            } else {
                holder.image.visibility = View.GONE
            }


            if (!review.profile_image.isNullOrEmpty()) {
                Glide.with(holder.itemView.context)
                    .load(review.profile_image)
                    .into(holder.userProfile)
            } else {
                holder.userProfile.setImageResource(R.drawable.ic_profile_placeholder)
            }
        }

        override fun getItemCount() = reviews.size
    }
}
