from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from app.models import User

class LoginForm(FlaskForm):
    """로그인 폼"""
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    remember = BooleanField('로그인 상태 유지')
    submit = SubmitField('로그인')

class RegisterForm(FlaskForm):
    """회원가입 폼"""
    username = StringField('닉네임', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('비밀번호 확인', 
                                    validators=[DataRequired(), EqualTo('password', message='비밀번호가 일치하지 않습니다.')])
    real_name = StringField('이름', validators=[Length(max=100)])
    phone_number = StringField('전화번호', validators=[Length(max=20)])
    
    # 약관 동의 필드는 동적으로 추가됨
    
    submit = SubmitField('회원가입')
    
    def validate_username(self, username):
        """닉네임 중복 확인"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 사용 중인 닉네임입니다. 다른 닉네임을 사용해주세요.')
    
    def validate_email(self, email):
        """이메일 중복 확인"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.')

class ProfileForm(FlaskForm):
    """프로필 수정 폼"""
    username = StringField('닉네임', validators=[DataRequired(), Length(min=2, max=20)])
    real_name = StringField('이름', validators=[Length(max=100)])
    phone_number = StringField('전화번호', validators=[Length(max=20)])
    profile_image = FileField('프로필 이미지', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    bio = TextAreaField('자기소개', validators=[Length(max=500)])
    submit = SubmitField('정보 수정')
    
    def validate_username(self, username):
        """닉네임 중복 확인 (현재 사용자 제외)"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('이미 사용 중인 닉네임입니다. 다른 닉네임을 사용해주세요.')

class ChangePasswordForm(FlaskForm):
    """비밀번호 변경 폼"""
    current_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    password = PasswordField('새 비밀번호', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('새 비밀번호 확인', 
                                    validators=[DataRequired(), EqualTo('password', message='비밀번호가 일치하지 않습니다.')])
    submit = SubmitField('비밀번호 변경')