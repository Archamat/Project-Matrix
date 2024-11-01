from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProjectCreationForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    sector = SelectField('Sector', choices=[('web', 'Web'), ('ai', 'AI'), ('embedded', 'Embedded')], validators=[DataRequired()])
    people_count = IntegerField('Number of People', validators=[DataRequired(), NumberRange(min=1, max=16, message="Choose between 1 and 16")])
    skills = SelectMultipleField('Skills', choices=[
        ('C', 'C'), ('C++', 'C++'), ('C#', 'C#'), ('Python', 'Python'), ('Java', 'Java'), ('Other', 'Other')
    ], validators=[DataRequired()])
    other_skill = StringField('Other Skill')  # Additional field for custom skill input
    submit = SubmitField('Create Project')
