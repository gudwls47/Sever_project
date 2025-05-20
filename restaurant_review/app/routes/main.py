from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from sqlalchemy import func, or_, desc

from app import db
from app.models import User, Restaurant, Review, UserScore

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """메인 페이지 - 리뷰어 온도 순위와 리뷰 갯수 순위를 보여줌"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents)
    
    # 강제로 모바일/데스크톱 모드를 설정한 경우
    view_mode = request.args.get('view') or session.get('view_mode')
    if view_mode:
        session['view_mode'] = view_mode
        is_mobile = (view_mode == 'mobile')
    
    # 리뷰어 온도 기준 상위 5명
    top_reviewers_by_temperature = (
        User.query.join(UserScore, User.user_id == UserScore.user_id)
        .filter(User.is_active == True)
        .order_by(UserScore.trust_score.desc())
        .limit(5)
        .all()
    )
    
    # 리뷰 갯수 기준 상위 5명
    top_reviewers_by_reviews = (
        User.query.join(UserScore, User.user_id == UserScore.user_id)
        .filter(User.is_active == True)
        .order_by(UserScore.review_count.desc())
        .limit(5)
        .all()
    )
    
    # 평점 높은 맛집 5곳
    top_restaurants = (
        Restaurant.query
        .filter(Restaurant.average_rating > 0)
        .order_by(Restaurant.average_rating.desc())
        .limit(5)
        .all()
    )
    
    # 최근 리뷰 5개
    recent_reviews = (
        Review.query
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )
    
    if is_mobile:
        return render_template(
            'main/mobile_index.html',
            top_reviewers_by_temperature=top_reviewers_by_temperature,
            top_reviewers_by_reviews=top_reviewers_by_reviews,
            top_restaurants=top_restaurants,
            recent_reviews=recent_reviews
        )
    else:
        return render_template(
            'main/index.html',
            top_reviewers_by_temperature=top_reviewers_by_temperature,
            top_reviewers_by_reviews=top_reviewers_by_reviews,
            top_restaurants=top_restaurants,
            recent_reviews=recent_reviews
        )

@main_bp.route('/search')
def search():
    """검색 결과 페이지"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    query = request.args.get('query', '')
    filter_by = request.args.get('filter', 'restaurants')  # restaurants, reviewers
    sort_by = request.args.get('sort', 'rating')  # rating, reviews
    category = request.args.get('category', '')  # 카테고리 필터
    location = request.args.get('location', '')  # 지역 필터
    
    if not query and not category and not location:
        return redirect(url_for('main.index'))
    
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if filter_by == 'restaurants':
        # 맛집 검색 쿼리 작성
        query_obj = Restaurant.query
        
        # 검색어 필터
        if query:
            # 맛집 이름, 카테고리, 주소에서 검색
            query_obj = query_obj.filter(
                or_(
                    Restaurant.name.ilike(f'%{query}%'),
                    Restaurant.category.ilike(f'%{query}%'),
                    Restaurant.address.ilike(f'%{query}%')
                )
            )
        
        # 카테고리 필터
        if category:
            query_obj = query_obj.filter(Restaurant.category == category)
            
        # 지역 필터
        if location:
            query_obj = query_obj.filter(Restaurant.address.ilike(f'%{location}%'))
            
        # 정렬 적용
        if sort_by == 'rating':
            query_obj = query_obj.order_by(Restaurant.average_rating.desc())
        else:  # reviews
            # 리뷰수로 정렬
            review_count = db.session.query(
                Review.restaurant_id, 
                func.count(Review.review_id).label('count')
            ).group_by(Review.restaurant_id).subquery()
            
            query_obj = query_obj.outerjoin(
                review_count, 
                Restaurant.restaurant_id == review_count.c.restaurant_id
            ).order_by(desc(func.coalesce(review_count.c.count, 0)))
        
        # 페이지네이션 적용
        pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
        results = pagination.items
        
        # 검색없이 카테고리나 지역 필터만 있는 경우 메시지 추가
        search_message = ''
        if not query and (category or location):
            filter_terms = []
            if category:
                filter_terms.append(f'"{category}" 카테고리')
            if location:
                filter_terms.append(f'"{location}" 지역')
            
            search_message = ', '.join(filter_terms) + '에 해당하는 맛집입니다.'
        
        # 카테고리 목록 (필터용)
        categories = db.session.query(Restaurant.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        # 지역 목록 (필터용)
        locations = db.session.query(
            func.substring_index(Restaurant.address, ' ', 2).label('location')
        ).distinct().all()
        locations = [l[0] for l in locations if l[0]]
        
        template = 'main/mobile_search_results.html' if is_mobile else 'main/search_results.html'
        
        return render_template(
            template, 
            query=query,
            filter_by=filter_by,
            sort_by=sort_by,
            category=category,
            location=location,
            results=results,
            result_type='restaurants',
            pagination=pagination,
            search_message=search_message,
            categories=categories,
            locations=locations
        )
    
    else:  # reviewers
        # 리뷰어 검색 쿼리 작성
        query_obj = User.query.filter(User.is_active == True)
        
        # 검색어 필터
        if query:
            query_obj = query_obj.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.real_name.ilike(f'%{query}%')
                )
            )
        
        # 정렬 적용
        query_obj = query_obj.join(UserScore, User.user_id == UserScore.user_id, isouter=True)
        
        if sort_by == 'rating':
            query_obj = query_obj.order_by(UserScore.trust_score.desc())
        else:  # reviews
            query_obj = query_obj.order_by(UserScore.review_count.desc())
        
        # 페이지네이션 적용
        pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
        results = pagination.items
        
        template = 'main/mobile_search_results.html' if is_mobile else 'main/search_results.html'
        
        return render_template(
            template, 
            query=query,
            filter_by=filter_by,
            sort_by=sort_by,
            results=results,
            result_type='reviewers',
            pagination=pagination
        )

@main_bp.route('/about')
def about():
    """서비스 소개 페이지"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    template = 'main/mobile_about.html' if is_mobile else 'main/about.html'
    return render_template(template)

@main_bp.route('/notifications')
def notifications():
    """알림 페이지"""
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    # 여기서 알림 데이터를 가져오는 로직이 들어갈 수 있음
    
    template = 'main/mobile_notifications.html' if is_mobile else 'main/notifications.html'
    return render_template(template)
