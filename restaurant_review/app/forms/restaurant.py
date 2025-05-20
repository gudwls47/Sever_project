from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class RestaurantForm(FlaskForm):
    """맛집 등록/수정 폼"""
    name = StringField('상호명', validators=[DataRequired(), Length(max=100)])
    address = StringField('주소', validators=[DataRequired(), Length(max=255)])
    category = SelectField('카테고리', choices=[
        ('한식', '한식'),
        ('중식', '중식'),
        ('일식', '일식'),
        ('양식', '양식'),
        ('분식', '분식'),
        ('카페', '카페'),
        ('베이커리', '베이커리'),
        ('기타', '기타')
    ])
    phone = StringField('전화번호', validators=[Length(max=20)])
    latitude = FloatField('위도', validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude = FloatField('경도', validators=[Optional(), NumberRange(min=-180, max=180)])
    tags = SelectMultipleField('태그', coerce=int)