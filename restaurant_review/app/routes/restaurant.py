from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import func

from app import db
from app.models import Restaurant, Review, ReviewDetail, Tag
from app.forms.restaurant import RestaurantForm

restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/restaurant')

@restaurant_bp.route('/')
def index():
    """맛집 목록 페이지"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    # 정렬 및 필터 옵션
    sort_by = request.args.get('sort_by', 'rating')  # rating, reviews
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    
    # 기본 쿼리
    query = Restaurant.query
    
    # 필터 적용
    if category:
        query = query.filter(Restaurant.category == category)
    
    if location:
        query = query.filter(Restaurant.address.ilike(f'%{location}%'))
    
    # 정렬 적용
    if sort_by == 'rating':
        query = query.order_by(Restaurant.average_rating.desc())
    elif sort_by == 'reviews':
        query = query.outerjoin(Review).group_by(Restaurant.restaurant_id).order_by(func.count(Review.review_id).desc())
    
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    restaurants = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 카테고리 목록 (필터용)
    categories = db.session.query(Restaurant.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # 지역 목록 (필터용)
    locations = db.session.query(
        func.substring_index(Restaurant.address, ' ', 2).label('location')
    ).distinct().all()
    locations = [l[0] for l in locations if l[0]]
    
    template = 'restaurant/mobile_index.html' if is_mobile else 'restaurant/index.html'
    
    return render_template(
        template,
        restaurants=restaurants,
        categories=categories,
        locations=locations,
        sort_by=sort_by,
        category=category,
        location=location
    )

@restaurant_bp.route('/<int:restaurant_id>')
def detail(restaurant_id):
    """맛집 상세 정보 페이지"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # 리뷰 정보
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).all()
    
    # 별점 통계
    rating_stats = {
        'avg': restaurant.average_rating,
        'count': len(reviews),
        'distribution': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    }
    
    for review in reviews:
        if review.rating in rating_stats['distribution']:
            rating_stats['distribution'][review.rating] += 1
    
    # 항목별 평가 평균
    taste_avg = db.session.query(func.avg(ReviewDetail.taste_rating)).filter(
        ReviewDetail.review_id.in_([r.review_id for r in reviews])
    ).scalar() or 0
    
    price_avg = db.session.query(func.avg(ReviewDetail.price_rating)).filter(
        ReviewDetail.review_id.in_([r.review_id for r in reviews])
    ).scalar() or 0
    
    service_avg = db.session.query(func.avg(ReviewDetail.service_rating)).filter(
        ReviewDetail.review_id.in_([r.review_id for r in reviews])
    ).scalar() or 0
    
    # 관련 태그
    tags = restaurant.tags
    
    template = 'restaurant/mobile_detail.html' if is_mobile else 'restaurant/detail.html'
    
    return render_template(
        template,
        restaurant=restaurant,
        reviews=reviews,
        rating_stats=rating_stats,
        taste_avg=taste_avg,
        price_avg=price_avg,
        service_avg=service_avg,
        tags=tags
    )

@restaurant_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """맛집 등록 페이지 (사장님 전용)"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    # 사장님만 접근 가능하도록 확인
    if current_user.user_type != 'admin':
        flash('맛집 등록은 사장님 계정으로만 가능합니다.', 'danger')
        return redirect(url_for('restaurant.index'))
    
    form = RestaurantForm()
    
    # 태그 선택 목록 생성
    all_tags = Tag.query.all()
    form.tags.choices = [(tag.tag_id, tag.name) for tag in all_tags]
    
    if form.validate_on_submit():
        restaurant = Restaurant(
            name=form.name.data,
            address=form.address.data,
            category=form.category.data,
            phone=form.phone.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        
        # 태그 연결
        selected_tags = Tag.query.filter(Tag.tag_id.in_(form.tags.data)).all()
        restaurant.tags = selected_tags
        
        db.session.add(restaurant)
        db.session.commit()
        
        flash('맛집이 등록되었습니다.', 'success')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant.restaurant_id))
    
    template = 'restaurant/mobile_create.html' if is_mobile else 'restaurant/create.html'
    return render_template(template, form=form)

@restaurant_bp.route('/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(restaurant_id):
    """맛집 정보 수정 페이지 (사장님 전용)"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    # 사장님만 접근 가능하도록 확인
    if current_user.user_type != 'admin':
        flash('맛집 정보 수정은 사장님 계정으로만 가능합니다.', 'danger')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant_id))
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = RestaurantForm(obj=restaurant)
    
    # 태그 선택 목록 생성
    all_tags = Tag.query.all()
    form.tags.choices = [(tag.tag_id, tag.name) for tag in all_tags]
    
    if request.method == 'GET':
        # 기존 태그 선택
        form.tags.data = [tag.tag_id for tag in restaurant.tags]
    
    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.address = form.address.data
        restaurant.category = form.category.data
        restaurant.phone = form.phone.data
        restaurant.latitude = form.latitude.data
        restaurant.longitude = form.longitude.data
        
        # 태그 업데이트
        selected_tags = Tag.query.filter(Tag.tag_id.in_(form.tags.data)).all()
        restaurant.tags = selected_tags
        
        db.session.commit()
        
        flash('맛집 정보가 수정되었습니다.', 'success')
        return redirect(url_for('restaurant.detail', restaurant_id=restaurant.restaurant_id))
    
    template = 'restaurant/mobile_edit.html' if is_mobile else 'restaurant/edit.html'
    return render_template(template, form=form, restaurant=restaurant)

@restaurant_bp.route('/map')
def map_view():
    """지도 기반 맛집 보기"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    # 지도 API 키 (환경 변수에서 가져옴)
    map_api_key = current_app.config.get('MAP_API_KEY', '')
    
    # 모든 맛집의 위치 데이터
    restaurants = Restaurant.query.filter(
        Restaurant.latitude.isnot(None),
        Restaurant.longitude.isnot(None)
    ).all()
    
    # 지도에 표시할 데이터 포맷
    map_data = []
    for r in restaurants:
        map_data.append({
            'id': r.restaurant_id,
            'name': r.name,
            'lat': float(r.latitude),
            'lng': float(r.longitude),
            'rating': r.average_rating,
            'category': r.category
        })
    
    template = 'restaurant/mobile_map.html' if is_mobile else 'restaurant/map.html'
    return render_template(template, map_api_key=map_api_key, map_data=map_data)