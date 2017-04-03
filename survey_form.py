from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators, \
    TextAreaField, SelectField, RadioField

# Reference:
# http://pythonhosted.org/Flask-Bootstrap/forms.html

class SurveyQuestionForm(Form):
    HTML = '''
    <h1>Starchy Foods</h1>
    <a href="/survey/img/{{question_data['image_source']}}"" target="_blank">
        <img src="/survey/img/{{question_data['image_source']}}"" width="600">
    </a>
    <br>
    <br>
    <form class="form form-horizontal" method="post" role="form">
        {{ form.hidden_tag() }}
        {{ wtf.form_errors(form, hiddens="only") }}

        <label>
            {{form.is_starchy.label.text|safe}}
        </label>
        {{ wtf.form_field(form.is_starchy) }}
        {{ wtf.form_field(form.comments) }}

        <a href="/{{question_id-1}}" class="btn btn-primary" role="button">Previous</a>
        <button class="btn btn-primary" type=submit>Next</button>
    </form>
    '''

    comments = TextAreaField(u'Comments', validators=[validators.optional()])
    is_starchy = RadioField('Is there a significant source of starches in the image (e.g., bread, pasta, potatoes, rice)?',
                            [validators.Required()],
                            choices=[('yes', 'Yes'), ('no', 'No'), ('not_sure', 'Not sure')],
                            coerce=unicode)
