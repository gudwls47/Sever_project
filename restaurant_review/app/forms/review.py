from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed  # MultipleFileField 제거
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

# MultipleFileField 직접 구현
class MultipleFileField(FileField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist
        else:
            self.data = []
            
class ReviewForm(FlaskForm):
    """리뷰 작성/수정 폼"""
    rating = IntegerField('전체 평점', validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message='평점은 1-5 사이의 값이어야 합니다.')
    ])
    
    taste_rating = RadioField('맛 평가', choices=[
        ('1', '맛없음'),
        ('2', '보통'),
        ('3', '맛있음')
    ], validators=[DataRequired()])
    
    price_rating = RadioField('가격 평가', choices=[
        ('1', '비쌈'),
        ('2', '보통'),
        ('3', '쌈')
    ], validators=[DataRequired()])
    
    service_rating = RadioField('응대 평가', choices=[
        ('1', '불친절함'),
        ('2', '보통'),
        ('3', '친절함')
    ], validators=[DataRequired()])
    
    content = TextAreaField('리뷰 내용', validators=[
        DataRequired(), 
        Length(min=10, max=2000, message='리뷰는 10-2000자 사이로 작성해주세요.')
    ])
    
    images = MultipleFileField('리뷰 이미지 (최대 5장)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 업로드 가능합니다.')
    ])
    
    receipt_image = FileField('영수증 인증 이미지', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 업로드 가능합니다.')
    ])
    
    submit = SubmitField('리뷰 등록')
    
    def validate_images(self, field):
        """이미지 개수 제한 검증"""
        if field.data and len(field.data) > 5:
            raise ValueError('이미지는 최대 5장까지 업로드 가능합니다.')