#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2019/04/12 16:35:09
@Author  :   jiegemena 
@Version :   1.0
@Contact :   jiegemena@outlook.com
@License :   https://github.com/jiegemena
@Desc    :   None
'''

# here put the import lib
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2019/04/12 16:33:48
@Author  :   jiegemena 
@Version :   1.0
@Contact :   jiegemena@outlook.com
@License :   https://github.com/jiegemena
@Desc    :   None
'''

# here put the import lib
from flask import Flask, request
import os
from datetime import timedelta
from jgpycshare.LogTools import LogTools
import area
import json
import tools

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app():

    app = Flask(__name__)
    app.config.from_object('config')
    if app.config['DEBUG']:
        app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。

    app.secret_key = app.config['SECRET_KEY']

    flask_logging(app)
    flask_init(app)
    flask_blueprints(app)
    # register_commands(app)
    register_errors(app)
    # register_shell_context(app)
    flask_template_context(app)

    sql_intercept = app.config['REQUEST_INTERCEPT']
    sql_intercept = sql_intercept.split('|')
    flask_request_handlers(app, sql_intercept)
    return app


def flask_logging(app):
    log = tools.qxlog()
    app.config['log'] = log
    log.info("info")
    log.debug("debug")
    log.error("error")
    log.info("info")


# 初始化应用
def flask_init(app):
    if os.path.exists(app.config['SQL_INIT'] + '.lock') is False:
        file = open(app.config['SQL_INIT'] + '.lock', 'w')
        file.write('del it create new database!')
        file.close()

        db = tools.db_sqlite3(sql_conn_str=app.config['SQL_CONN'])
        with open(app.config['SQL_INIT'], 'r') as f:
            db.get_db().executescript(f.read())
            print("db init successfully")
    ### register consul
    tools.unregister()
    if app.config['CONSUL_STATE']:
        tools.register()


def flask_blueprints(app):
    # app.register_blueprint(area.api_bp, url_prefix='/api')
    # app.register_blueprint(area.admin_bp, url_prefix='/admin')
    app.register_blueprint(area.guest_bp, url_prefix='/')
    # app.register_blueprint(web_bp)


# def register_shell_context(app):
#     @app.shell_context_processor
#     def make_shell_context():
#         return dict(db='db')


# 可以在 模板处 : <a href="mailto:{{test}}">{{test}}</a>
def flask_template_context(app):
    @app.context_processor
    def make_template_context():
        return dict(test='test')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return '400 error'

    @app.errorhandler(404)
    def page_not_found(e):
        return '500 error'

    @app.errorhandler(500)
    def internal_server_error(e):
        return '500 error'


def flask_request_handlers(app, sql_intercept):
    @app.after_request
    def after_request(response):
        # token = 'asdfaasdf'
        # response.set_cookie('csrf_token', token)
        # print('request end')
        return response

    @app.before_request
    def print_request_info():
        log = app.config['log']
        log.info("请求地址:" + str(request.path))
        log.info("GET参数：" + str(request.args))
        log.info("POST参数：" + str(request.form))
        for key in request.args:
            for k in sql_intercept:
                if (request.args[key]).find(k) >= 0:
                    return 'have get sql_intercept par:' + k

        for key in request.form:
            for k in sql_intercept:
                if (request.form[key]).find(k) >= 0:
                    return 'have post sql_intercept par:' + k
        