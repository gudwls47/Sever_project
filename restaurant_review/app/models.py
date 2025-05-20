from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager

# 사용자 로드 함수 (Flask-Login 용)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 태그 연결 테이블
restaurant_tags = db.Table('restaurant_tags',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurant.restaurant_id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'), primary_key=True)
)

# 사용자 테이블
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    user_type = db.Column(db.Enum('normal', 'admin', name='user_types'), default='normal')
    trust_score = db.Column(db.Integer, default=0)
    activity_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 관계 설정
    reviews = db.relationship('Review', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    
    def __init__(self, username, email, password, real_name=None, phone_number=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.real_name = real_name
        self.phone_number = phone_number
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)
    
    def __repr__(self):
        return f'<User {self.username}>'

# 맛집 정보 테이블
class Restaurant(db.Model):
    restaurant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    average_rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    reviews = db.relationship('Review', backref='restaurant', lazy=True)
    tags = db.relationship('Tag', secondary=restaurant_tags, backref=db.backref('restaurants', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'

# 태그 테이블
class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Tag {self.name}>'

# 리뷰 테이블
class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.restaurant_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    receipt_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 관계 설정
    likes = db.relationship('Like', backref='review', lazy=True)
    images = db.relationship('ReviewImage', backref='review', lazy=True)
    details = db.relationship('ReviewDetail', backref='review', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Review {self.review_id} by User {self.user_id}>'

# 리뷰 항목별 평가 테이블
class ReviewDetail(db.Model):
    review_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), primary_key=True)
    taste_rating = db.Column(db.Integer)
    price_rating = db.Column(db.Integer)
    service_rating = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<ReviewDetail for Review {self.review_id}>'

# 리뷰 이미지 테이블
class ReviewImage(db.Model):
    review_image_id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<ReviewImage {self.review_image_id}>'

# 좋아요 테이블
class Like(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Like by User {self.user_id} on Review {self.review_id}>'

# 사용자 점수 테이블 (랭킹용)
class UserScore(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    review_count = db.Column(db.Integer, default=0)
    like_received_count = db.Column(db.Integer, default=0)
    receipt_verified_count = db.Column(db.Integer, default=0)
    trust_score = db.Column(db.Integer, default=0)
    activity_score = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('score', uselist=False))
    
    def __repr__(self):
        return f'<UserScore for User {self.user_id}>'

# 약관 테이블
class Terms(db.Model):
    terms_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    agreements = db.relationship('UserAgreement', backref='terms', lazy=True)
    
    def __repr__(self):
        return f'<Terms {self.title}>'

# 사용자 약관 동의 기록 테이블
class UserAgreement(db.Model):
    agreement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    terms_id = db.Column(db.Integer, db.ForeignKey('terms.terms_id'), nullable=False)
    agreed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('agreements', lazy=True))
    
    def __repr__(self):
        return f'<UserAgreement by User {self.user_id} for Terms {self.terms_id}>'


# 리뷰어 온도 평가 테이블
class ReviewerRating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rater = db.relationship('User', foreign_keys=[rater_id], backref=db.backref('ratings_given', lazy=True))
    target = db.relationship('User', foreign_keys=[target_id], backref=db.backref('ratings_received', lazy=True))
    
    def __repr__(self):
        return f'<ReviewerRating by User {self.rater_id} for User {self.target_id}>'