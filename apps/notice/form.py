from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms import DateField

class NoticeForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    author = StringField('작성자명',validators=[DataRequired()]) 
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('작성')
