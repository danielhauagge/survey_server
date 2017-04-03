from wtforms import TextField, PasswordField
from wtforms.validators import Required

from flask_login import login_user, logout_user, current_user, login_required
from flask import request, render_template, g, flash, redirect, url_for
from flask_wtf import Form

from surveys import app, db, lm
from models import User

class LoginForm(Form):
    username = TextField('Userame', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if g.user is not None and g.user.is_authenticated():
    #     if g.user.is_admin == True:
    #         return redirect(url_for('administrator'))
    #     else:
    #         return redirect(url_for('user', username=g.user.username))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if (user is not None and user.password == form.password.data):
            login_user(user)
            flash("Login successfully")
            return redirect(url_for('get_survey_'))

        form.password.data = ''
        flash("Login failed", 'error')

    return render_template('login.html', g=g, form=form, islogin=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
