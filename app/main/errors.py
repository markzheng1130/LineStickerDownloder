from flask import render_template

from app.main import blueprint_main

@blueprint_main.app_errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400

@blueprint_main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
