#!/usr/bin/env python

from flask import Flask, jsonify, make_response, request, abort, send_file, \
                  render_template, send_from_directory, redirect, json, url_for
import flask_login

from sqlalchemy.sql import exists

import argparse
import urllib2
import logging
import sys
from getpass import getpass
from colorama import Fore

from surveys import app, db, encode_json
from surveys.models import User, SurveyQuestion, SurveyAnswer

# ============================================================================ #
# TODO                                                                         #
# ============================================================================ #
# [ ] Hash passwords: http://flask.pocoo.org/snippets/54/

# ============================================================================ #
# Globals                                                                      #
# ============================================================================ #

# Configuration
DEFAULT_PORT = 5555

# ============================================================================ #
# Methods                                                                      #
# ============================================================================ #


class LogFormatter(logging.Formatter):

    base_fmt = '[SurveyServer] %(asctime)s %(levelname)5s: %(message)s'
    err_fmt = Fore.RED + base_fmt.format(levelname="ERROR") + Fore.RESET
    dbg_fmt = base_fmt.format(levelname="DEBUG")
    info_fmt = base_fmt.format(levelname="INFO")
    warn_fmt = Fore.YELLOW + base_fmt.format(levelname="WARN") + Fore.RESET

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = LogFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._fmt = LogFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = LogFormatter.err_fmt

        elif record.levelno == logging.WARNING:
            self._fmt = LogFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


def init_logger():
    '''Initialize the logger, call at the begining of main.
    '''
    fmt = LogFormatter()
    hdlr = logging.StreamHandler(sys.stdout)

    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.DEBUG)

    logging.addLevelName(logging.WARNING, 'WARN')


def get_public_hostname():
    return urllib2.urlopen('https://api.ipify.org?format=text').read()


def main_run(port, mode_args, debug):
    port = args['port']

    logging.info('=' * 80)
    logging.info('Listening on http://%s:%d', get_public_hostname(), port)
    logging.info('=' * 80)

    app.run(port=port, host='0.0.0.0', debug=debug, threaded=True)


def main_add_data(mode_args):
    data_fname = mode_args[0]

    data = json.loads(open(data_fname, 'r').read())

    logging.info('Loaded %d records from %s', len(data), data_fname)

    n_added = 0
    for i, record in enumerate(data):
        json_record = encode_json(record)

        if db.session.query(exists().where(SurveyQuestion.data_json == json_record)).scalar():
            logging.warn('Skiping line %d, already exists', i)
            continue

        question = SurveyQuestion(data_json=json_record)
        db.session.add(question)
        n_added += 1

    logging.info('Added %d/%d of the records on file', n_added, len(data))

    db.session.commit()


def main_add_user(mode_args):
    username = mode_args[0]
    password = getpass('Password for user "%s": ' % (username))
    password_confirm = getpass('Confirm password: ')

    if password != password_confirm:
        logging.error("Passwords didn't match")
        sys.exit(1)

    user = User(name=username, password=password)
    db.session.add(user)
    db.session.commit()


def main_list_users(mode_args):
    for user in User.query.order_by(User.name).all():
        # user.get_unanswered_questions()
        print '[%4d] %-9s: %4d/%d' % (user.id, user.name, user.get_answered_questions().count(), len(SurveyQuestion.query.all()))


def main_create_db(mode_args):
    db.create_all()


def main_data_info(mode_args):
    print '%d questions to answer' % (len(SurveyQuestion.query.all()))


def main_save_results(mode_args):
    output_fname = mode_args[0]

    res = db.session.query(User.name, SurveyQuestion.data_json, SurveyAnswer.answer_json). \
        filter(User.id == SurveyAnswer.user_id). \
        filter(SurveyAnswer.question_id == SurveyQuestion.id)

    results = []
    for user_name, question_json, answer_json in res:
        question = json.loads(question_json)
        answer = json.loads(answer_json)

        result = {'user_name': user_name, 'question': question, 'answer': answer}
        results.append(result)

    logging.info('Saving %d records to %s', len(results), output_fname)

    with open(output_fname, 'w') as f:
        f.write(json.dumps(results))

# ============================================================================ #
# Main                                                                         #
# ============================================================================ #
if __name__ == '__main__':
    init_logger()

    # Command line options
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', help='Mode of operation, can be one of "add_data", "add_user", "run", "create_db", "ls_users", "data_info".')
    parser.add_argument('mode_args', nargs='*', help='Arguments for given operation.')
    parser.add_argument(
        "--port", default=DEFAULT_PORT, type=int,
        help="Which port to listen on [default = %(default)d]."
    )
    parser.add_argument(
        "--debug", default=False, action='store_true',
        help="Run in debug mode."
    )

    args = vars(parser.parse_args())
    mode = args['mode']
    mode_args = args['mode_args']

    port = args['port']

    if mode == 'run':
        main_run(port, mode_args, args['debug'])
    elif mode == 'add_user':
        main_add_user(mode_args)
    elif mode == 'add_data':
        main_add_data(mode_args)
    elif mode == 'create_db':
        main_create_db(mode_args)
    elif mode == 'ls_users':
        main_list_users(mode_args)
    elif mode == 'data_info':
        main_data_info(mode_args)
    elif mode == 'results':
        main_save_results(mode_args)
    else:
        print 'Wrong usage, run with -h for help'
        sys.exit(1)
