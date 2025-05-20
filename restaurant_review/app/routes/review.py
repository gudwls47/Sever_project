from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from app import db
from app.models import Restaurant, Review, ReviewDetail, ReviewImage, Like, User, UserScore, ReviewerRating
from app.forms.review import ReviewForm

review_bp = Blueprint('review', __name__, url_prefix='/review')

@review_bp.route('/<int:review_id>')
def detail(review_id):
    """리뷰 상세 페이지"""
    review = Review.query.get_or_404(review_id)
    
    # 리뷰 좋아요 여부 확인
    liked = False
    if current_user.is_authenticated:
        like = Like.query.filter_by(user_id=current_user.user_id, review_id=review_id).first()
        liked = like is not None
    
    return render_template('review/detail.html', review=review, liked=liked)

@review_bp.route('/create/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def create(restaurant_id):
    """리뷰 작성 페이지"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # 리뷰 생성
        review = Review(
            user_id=current_user.user_id,
            restaurant_id=restaurant_id,
            rating=form.rating.data,
            content=form.content.data
        )
        db.session.add(review)
        db.session.flush()  # 리뷰 ID를 얻기 위해 flush
        
        # 항목별 평가 저장
        review_detail = ReviewDetail(
            review_id=review.review_id,
            taste_rating=form.taste_rating.data,
            price_rating=form.price_rating.data,
            service_rating=form.service_rating.data
        )
        db.session.add(review_detail)
        
        # 이미지 업로드 처리
        if form.images.data:
            for image in form.images.data:
                if image.filename:
                    filename = secure_filename(image.filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                        flash('지원되지 않는 이미지 형식입니다. JPG, JPEG, PNG, GIF만 허용됩니다.', 'danger')
                        continue
                    
                    # 고유한 파일명 생성
                    unique_filename = f"review_{review.review_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reviews', unique_filename)
                    
                    # 디렉토리 생성
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # 파일 저장
                    image.save(file_path)
                    
                    # DB에 이미지 정보 저장
                    review_image = ReviewImage(
                        review_id=review.review_id,
                        image_url=f'/static/uploads/reviews/{unique_filename}'
                    )
                    db.session.add(review_image)
        
        # 영수증 인증 처리
        if form.receipt_image.data:
            filename = secure_filename(form.receipt_image.data.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                flash('지원되지 않는 이미지 형식입니다. JPG, JPEG, PNG, GIF만 허용됩니다.', 'danger')
            else:
                # 고유한 파일명 생성
                unique_filename = f"receipt_{review.review_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'receipts', unique_filename)
                
                # 디렉토리 생성
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 파일 저장
                form.receipt_image.data.save(file_path)
                
                # 영수증 이미지 경로 저장
                review.image_url = f'/static/uploads/receipts/{unique_filename}'
                review.receipt_verified = True
        
        # 리뷰어 통계 업데이트
        user_score = UserScore.query.filter_by(user_id=current_user.user_id).first()
        if not user_score:
            user_score = UserScore(user_id=current_user.user_id)
            db.session.add(user_score)
        
        user_score.review_count += 1
        if review.receipt_verified:
            user_score.receipt_verified_count += 1
        
        # 맛집 평균 평점 업데이트
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(restaurant_id=restaurant_id).scalar() or 0
        restaurant.average_rating = avg_rating
        
        db.session.commit()
        
        flash('리뷰가 등록되었습니다.', 'success')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
    
    return render_template('review/create.html', form=form, restaurant=restaurant)

@review_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    """리뷰 수정 페이지"""
    review = Review.query.get_or_404(review_id)
    
    # 자신의 리뷰만 수정 가능
    if review.user_id != current_user.user_id:
        flash('자신이 작성한 리뷰만 수정할 수 있습니다.', 'danger')
        return redirect(url_for('review.detail', review_id=review_id))
    
    form = ReviewForm(obj=review)
    
    # 항목별 평가 데이터 가져오기
    if review.details:
        form.taste_rating.data = review.details.taste_rating
        form.price_rating.data = review.details.price_rating
        form.service_rating.data = review.details.service_rating
    
    if form.validate_on_submit():
        # 리뷰 업데이트
        review.rating = form.rating.data
        review.content = form.content.data
        
        # 항목별 평가 업데이트
        if not review.details:
            review.details = ReviewDetail(review_id=review.review_id)
        
        review.details.taste_rating = form.taste_rating.data
        review.details.price_rating = form.price_rating.data
        review.details.service_rating = form.service_rating.data
        
        # 이미지 업로드 처리 (추가 이미지)
        if form.images.data:
            for image in form.images.data:
                if image.filename:
                    filename = secure_filename(image.filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                        flash('지원되지 않는 이미지 형식입니다. JPG, JPEG, PNG, GIF만 허용됩니다.', 'danger')
                        continue
                    
                    # 고유한 파일명 생성
                    unique_filename = f"review_{review.review_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reviews', unique_filename)
                    
                    # 디렉토리 생성
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # 파일 저장
                    image.save(file_path)
                    
                    # DB에 이미지 정보 저장
                    review_image = ReviewImage(
                        review_id=review.review_id,
                        image_url=f'/static/uploads/reviews/{unique_filename}'
                    )
                    db.session.add(review_image)
        
        # 맛집 평균 평점 업데이트
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(restaurant_id=review.restaurant_id).scalar() or 0
        review.restaurant.average_rating = avg_rating
        
        db.session.commit()
        
        flash('리뷰가 수정되었습니다.', 'success')
        return redirect(url_for('review.detail', review_id=review_id))
    
    return render_template('review/edit.html', form=form, review=review)

@review_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete(review_id):
    """리뷰 삭제"""
    review = Review.query.get_or_404(review_id)
    
    # 자신의 리뷰만 삭제 가능
    if review.user_id != current_user.user_id and current_user.user_type != 'admin':
        flash('자신이 작성한 리뷰만 삭제할 수 있습니다.', 'danger')
        return redirect(url_for('review.detail', review_id=review_id))
    
    restaurant_id = review.restaurant_id
    
    # 사용자 통계 업데이트
    user_score = UserScore.query.filter_by(user_id=review.user_id).first()
    if user_score:
        user_score.review_count = max(0, user_score.review_count - 1)
        if review.receipt_verified:
            user_score.receipt_verified_count = max(0, user_score.receipt_verified_count - 1)
    
    # 리뷰 삭제
    db.session.delete(review)
    
    # 맛집 평균 평점 업데이트
    remaining_reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
    if remaining_reviews:
        avg_rating = sum([r.rating for r in remaining_reviews]) / len(remaining_reviews)
    else:
        avg_rating = 0
    
    restaurant = Restaurant.query.get(restaurant_id)
    restaurant.average_rating = avg_rating
    
    db.session.commit()
    
    flash('리뷰가 삭제되었습니다.', 'success')
    return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))

@review_bp.route('/like/<int:review_id>', methods=['POST'])
@login_required
def like(review_id):
    """리뷰 좋아요 토글"""
    review = Review.query.get_or_404(review_id)
    
    # 자신의 리뷰는 좋아요 불가
    if review.user_id == current_user.user_id:
        return jsonify({'success': False, 'message': '자신의 리뷰는 좋아요할 수 없습니다.'})
    
    like = Like.query.filter_by(user_id=current_user.user_id, review_id=review_id).first()
    
    if like:
        # 좋아요 취소
        db.session.delete(like)
        
        # 좋아요 수 감소
        user_score = UserScore.query.filter_by(user_id=review.user_id).first()
        if user_score:
            user_score.like_received_count = max(0, user_score.like_received_count - 1)
        
        db.session.commit()
        return jsonify({'success': True, 'liked': False})
    else:
        # 좋아요 추가
        like = Like(user_id=current_user.user_id, review_id=review_id)
        db.session.add(like)
        
        # 좋아요 수 증가 및 신뢰 점수 업데이트
        user_score = UserScore.query.filter_by(user_id=review.user_id).first()
        if not user_score:
            user_score = UserScore(user_id=review.user_id)
            db.session.add(user_score)
        
        user_score.like_received_count += 1
        
        # 신뢰 점수 계산 (예: 리뷰 수, 인증 리뷰 수, 좋아요 수 등 고려)
        calculate_trust_score(review.user_id)
        
        db.session.commit()
        return jsonify({'success': True, 'liked': True})

@review_bp.route('/reviewer/<int:user_id>')
def reviewer(user_id):
    """리뷰어 프로필 페이지"""
    user = User.query.get_or_404(user_id)
    
    # 리뷰어 정보
    user_score = UserScore.query.filter_by(user_id=user_id).first()
    if not user_score:
        user_score = UserScore(user_id=user_id)
        db.session.add(user_score)
        db.session.commit()
    
    # 리뷰 목록
    reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()
    
    # 리뷰 통계 가져오기
    review_stats = {}
    if reviews:
        # 평균 별점
        review_stats['avg_rating'] = sum([r.rating for r in reviews]) / len(reviews)
        
        # 한 달 내 작성한 리뷰 수
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        review_stats['recent_count'] = Review.query.filter(
            Review.user_id == user_id,
            Review.created_at >= one_month_ago
        ).count()
        
        # 별점 분포
        review_stats['rating_dist'] = {}
        for i in range(1, 6):
            review_stats['rating_dist'][i] = len([r for r in reviews if r.rating == i])
    
    # 자신의 프로필인지 확인
    is_own_profile = current_user.is_authenticated and current_user.user_id == user_id
    
    # 이미 평가했는지 확인
    has_rated = False
    if current_user.is_authenticated and not is_own_profile:
        # 평가 기록 확인 로직 (실제로는 데이터베이스에서 확인)
        # 예시: has_rated = ReviewerRating.query.filter_by(rater_id=current_user.user_id, target_id=user_id).first() is not None
        pass
    
    return render_template('review/reviewer.html', 
                         reviewer=user, 
                         user_score=user_score, 
                         reviews=reviews,
                         review_stats=review_stats,
                         is_own_profile=is_own_profile,
                         has_rated=has_rated)

@review_bp.route('/rate_reviewer/<int:reviewer_id>', methods=['POST'])
@login_required
def rate_reviewer(reviewer_id):
    """리뷰어 온도 평가"""
    # 자기 자신 평가 불가
    if reviewer_id == current_user.user_id:
        return jsonify({'success': False, 'message': '자신은 평가할 수 없습니다.'})
    
    # 리뷰어 존재 확인
    reviewer = User.query.get_or_404(reviewer_id)
    
    # 요청 데이터 가져오기
    data = request.json
    temperature = data.get('temperature', 0)
    feedback = data.get('feedback', '')
    
    if not temperature or not 0 <= int(temperature) <= 100:
        return jsonify({'success': False, 'message': '유효하지 않은 온도 값입니다.'})
    
    # 이미 평가했는지 확인
    existing_rating = ReviewerRating.query.filter_by(
        rater_id=current_user.user_id,
        target_id=reviewer_id
    ).first()
    
    if existing_rating:
        # 기존 평가 업데이트
        existing_rating.temperature = int(temperature)
        existing_rating.feedback = feedback
    else:
        # 새 평가 생성
        reviewer_rating = ReviewerRating(
            rater_id=current_user.user_id,
            target_id=reviewer_id,
            temperature=int(temperature),
            feedback=feedback
        )
        db.session.add(reviewer_rating)
    
    # 리뷰어 온도 업데이트
    user_score = UserScore.query.filter_by(user_id=reviewer_id).first()
    if not user_score:
        user_score = UserScore(user_id=reviewer_id)
        db.session.add(user_score)
    
    # 평가 평균 계산
    avg_rating = db.session.query(func.avg(ReviewerRating.temperature)).filter_by(target_id=reviewer_id).scalar() or 0
    
    # 리뷰어 점수 업데이트를 계산할 때 평가 평균 반영
    if existing_rating:
        # 기존 온도와 평균을 7:3으로 반영
        current_temp = user_score.trust_score or 0
        new_temp = (current_temp * 0.7) + (avg_rating * 0.3)
    else:
        # 평가 수가 적을 때는 평균에 더 가중치를 둠
        rating_count = ReviewerRating.query.filter_by(target_id=reviewer_id).count()
        if rating_count <= 3:
            # 평가가 적을 때는 평균에 더 비중을 둠
            new_temp = avg_rating
        else:
            # 평가가 많아질수록 기존 온도에 비중을 둠
            current_temp = user_score.trust_score or 0
            new_temp = (current_temp * 0.7) + (avg_rating * 0.3)
    
    user_score.trust_score = min(100, int(new_temp))
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '평가가 저장되었습니다.', 'new_temperature': user_score.trust_score})


def calculate_trust_score(user_id):
    """리뷰어 신뢰 점수 계산 함수"""
    user_score = UserScore.query.filter_by(user_id=user_id).first()
    if not user_score:
        return
    
    # 사용자의 리뷰 데이터
    review_count = user_score.review_count
    verified_count = user_score.receipt_verified_count
    like_count = user_score.like_received_count
    
    # 신뢰 점수 계산 (알고리즘 예시)
    # 기본 점수 + 인증 비율 + 좋아요 비율
    base_score = min(30, review_count * 2)  # 최대 30점
    
    verified_ratio = 0
    if review_count > 0:
        verified_ratio = (verified_count / review_count) * 40  # 최대 40점
    
    like_score = min(30, like_count)  # 최대 30점
    
    trust_score = base_score + verified_ratio + like_score
    trust_score = min(100, trust_score)  # 최대 100점으로 제한
    
    user_score.trust_score = int(trust_score)