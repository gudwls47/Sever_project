from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models import User, Terms, UserAgreement
from app.forms.auth import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    terms = Terms.query.filter_by(is_required=True).all()
    
    if form.validate_on_submit():
        # 약관 동의 확인
        required_terms = Terms.query.filter_by(is_required=True).count()
        agreed_terms = 0
        for field in form:
            if field.name.startswith('terms_') and field.data:
                agreed_terms += 1
        
        if agreed_terms < required_terms:
            flash('필수 약관에 모두 동의해야 합니다.', 'danger')
            template = 'auth/mobile_register.html' if is_mobile else 'auth/register.html'
            return render_template(template, form=form, terms=terms)
        
        # 사용자 생성
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            real_name=form.real_name.data,
            phone_number=form.phone_number.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 약관 동의 기록
        for term in terms:
            field_name = f'terms_{term.terms_id}'
            if hasattr(form, field_name) and getattr(form, field_name).data:
                agreement = UserAgreement(user_id=user.user_id, terms_id=term.terms_id)
                db.session.add(agreement)
        
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    template = 'auth/mobile_register.html' if is_mobile else 'auth/register.html'
    return render_template(template, form=form, terms=terms)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('이 계정은 비활성화되었습니다. 관리자에게 문의하세요.', 'danger')
                template = 'auth/mobile_login.html' if is_mobile else 'auth/login.html'
                return render_template(template, form=form)
            
            login_user(user, remember=form.remember.data)
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'danger')
    
    template = 'auth/mobile_login.html' if is_mobile else 'auth/login.html'
    return render_template(template, form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.real_name = form.real_name.data
        current_user.phone_number = form.phone_number.data
        
        # 프로필 이미지 처리
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                flash('지원되지 않는 이미지 형식입니다. JPG, JPEG, PNG, GIF만 허용됩니다.', 'danger')
                template = 'auth/mobile_profile.html' if is_mobile else 'auth/profile.html'
                return render_template(template, form=form)
            
            # 고유한 파일명 생성
            unique_filename = f"{current_user.user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 파일 저장
            form.profile_image.data.save(file_path)
            
            # 이전 프로필 이미지 삭제 로직 추가 가능
            
            # DB에 경로 저장
            current_user.profile_image = f'/static/uploads/profiles/{unique_filename}'
        
        db.session.commit()
        flash('프로필이 업데이트되었습니다.', 'success')
        return redirect(url_for('auth.profile'))
    
    template = 'auth/mobile_profile.html' if is_mobile else 'auth/profile.html'
    return render_template(template, form=form)

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.real_name = form.real_name.data
        current_user.phone_number = form.phone_number.data
        
        # 프로필 이미지 처리
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                flash('지원되지 않는 이미지 형식입니다. JPG, JPEG, PNG, GIF만 허용됩니다.', 'danger')
                template = 'auth/mobile_edit_profile.html' if is_mobile else 'auth/edit_profile.html'
                return render_template(template, form=form)
            
            # 고유한 파일명 생성
            unique_filename = f"{current_user.user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 파일 저장
            form.profile_image.data.save(file_path)
            
            # 이전 프로필 이미지 삭제 로직 추가 가능
            
            # DB에 경로 저장
            current_user.profile_image = f'/static/uploads/profiles/{unique_filename}'
        
        db.session.commit()
        flash('프로필이 업데이트되었습니다.', 'success')
        return redirect(url_for('auth.profile'))
    
    template = 'auth/mobile_edit_profile.html' if is_mobile else 'auth/edit_profile.html'
    return render_template(template, form=form)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # 모바일 기기 체크
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'ipod', 'android', 'mobile', 'tablet']
    is_mobile = any(agent in user_agent for agent in mobile_agents) or session.get('view_mode') == 'mobile'
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # 현재 비밀번호 확인
        if not current_user.check_password(form.current_password.data):
            flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
            template = 'auth/mobile_change_password.html' if is_mobile else 'auth/change_password.html'
            return render_template(template, form=form)
        
        # 새 비밀번호로 변경
        current_user.set_password(form.password.data)
        db.session.commit()
        
        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('auth.profile'))
    
    template = 'auth/mobile_change_password.html' if is_mobile else 'auth/change_password.html'
    return render_template(template, form=form)