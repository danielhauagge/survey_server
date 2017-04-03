import pickle
import logging
import json
import os

from flask import request, render_template, render_template_string, g, \
    flash, url_for, redirect
from flask.ext.login import current_user, login_required
# from wtforms import BooleanField, TextField, PasswordField, validators, \
#     TextAreaField, SelectField, RadioField
# from flask.ext.sqlalchemy import SQLAlchemy

# from werkzeug.datastructures import MultiDict

import wtforms_json
wtforms_json.init()

from survey_server import app, db, encode_json
from models import SurveyQuestion, SurveyAnswer, User

# We load the SurveyQuestionForm from the current working directory, this piece
# of code is provided by the user.
import importlib
survey_form_module = importlib.import_module('survey_form')
SurveyQuestionForm = survey_form_module.SurveyQuestionForm

# Reference:
# - On converting to and from to JSON: http://stackoverflow.com/questions/32062097/using-flask-wtforms-validators-without-using-a-form


def form_to_json(form):
    return encode_json(form.data)


def form_data_from_json(form, json_data):
    for key in json_data:
        if key in form.__dict__:
            form.__dict__[key].data = json_data[key]
        else:
            logging.warn('Key "%s" not in form objct, ignoring', key)


@app.route('/done')
@login_required
def done():
    n_surveys = SurveyQuestion.query.count()
    n_answers = User.query.get(current_user.id).get_answered_questions().count()

    if n_surveys == n_answers:
        flash("You are all done with the work!", "success")
        return render_template('base.html')
    else:
        flash("You still have work to do")
        return redirect(url_for('get_survey_'))


@app.route('/', methods=['GET'])
@login_required
def get_survey_():
    if 'question_id' not in g.__dict__:
        user = User.query.get(current_user.id)
        question = user.get_unanswered_questions().limit(1).all()

        if len(question) == 0:
            return redirect(url_for('done'))

        question = question[0]

        g.question_id = question.id
    else:
        g.question_id += 1

    return redirect(url_for('get_survey', question_id=question.id))


#request.remote_addr
@app.route('/<int:question_id>', methods=['GET', 'POST'])
@login_required
def get_survey(question_id):
    g.question_id = question_id

    question = SurveyQuestion.query.get(g.question_id)
    if question is None:
        return redirect(url_for('get_survey_'))

    question_data = json.loads(question.data_json)

    question_form = SurveyQuestionForm(request.form)

    if question_form.validate_on_submit():
        next_question_id = question_id + 1
        logging.warn('need to save survey reply')

        answer = question.get_user_answer(current_user.id)
        if answer:
            answer.answer_json = form_to_json(question_form)
            db.session.merge(answer)
        else:
            answer = SurveyAnswer(user_id=current_user.id, question_id=question.id, answer_json=form_to_json(question_form))
            db.session.add(answer)
            db.session.commit()

        return redirect(url_for('get_survey', question_id=question.id + 1))

    prev_user_answer = question.get_user_answer(current_user.id)
    if prev_user_answer is not None:
        logging.info('Logging previous answer')
        answer_json = json.loads(prev_user_answer.answer_json)
        form_data_from_json(question_form, answer_json)

    final_html = '''
    {{% extends "base.html" %}}
    {{% block body_contents %}}
        <div class="progress">
          <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: {{{{progress_perc}}}}%; min-width: 6em;">
            {{{{progress_msg}}}}
          </div>
        </div>

        {form_html}
    {{% endblock %}}
    '''.format(form_html=question_form.HTML)

    user = User.query.get(current_user.id)
    n_done = user.get_answered_questions().count()
    n_total = SurveyQuestion.query.count()

    progress_msg = '%d/%d done' % (n_done, n_total)
    progress_perc = 100.0 * float(n_done) / n_total

    return render_template_string(final_html, form=question_form,
        question_data=question_data, g=g, question_id=question.id,
        progress_perc=progress_perc, progress_msg=progress_msg)
