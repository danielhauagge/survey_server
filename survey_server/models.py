from . import db
from sqlalchemy.sql import exists
from sqlalchemy.sql import select
from sqlalchemy.orm import aliased
# References:
# http://lucumr.pocoo.org/2011/7/19/sqlachemy-and-you/
# http://alextechrants.blogspot.com/2013/11/10-common-stumbling-blocks-for.html
# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    password = db.Column(db.String(16))

    # Methods used by Login manager
    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def get_answered_questions(self):
        return db.session.query(SurveyQuestion).join(SurveyQuestion.answers).filter(self.id == SurveyAnswer.user_id)

    def get_unanswered_questions(self):
        answered = self.get_answered_questions().subquery()
        not_answered = db.session.query(SurveyQuestion).outerjoin(answered, answered.c.id == SurveyQuestion.id).filter(answered.c.id == None)
        return not_answered

    def __repr__(self):
        return '<User id:%r name:%r>' % (self.id, self.name)


class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_json = db.Column(db.Text, unique=True)

    def get_user_answer(self, user_id):
        return SurveyAnswer.query.get((user_id, self.id))
        # return db.session.query(SurveyAnswer). \
        #     filter(SurveyAnswer.question_id==self.id).get(1)

    def __repr__(self):
        return '<SurveyQuestion id:%r>' % (self.id)


class SurveyAnswer(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_question.id'), primary_key=True)

    create_time = db.Column(db.DateTime)
    answer_json = db.Column(db.Text)

    user = db.relationship('User', backref='answers')
    question = db.relationship('SurveyQuestion', backref="answers")

    def __repr__(self):
        return '<SurveyAnswer user_id:%r question_id:%r>' % (self.user_id, self.question_id)

    # user = db.relationship('User', backref='replies')
    # question = db.relationship('Question', backref='replies')
