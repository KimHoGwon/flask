from pathlib import Path
from flask import Flask,render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

from apps.config import config



db = SQLAlchemy()
csrf = CSRFProtect()
# LoginManager를 인스턴스화한다
login_manager = LoginManager()
# login_view 속성에 미로그인 시에 리다이렉트하는 엔드포인트를 지정한다
login_manager.login_view = "auth.login"
# login_message 속성에 로그인 후에 표시하는 메시지를 지정한다
# 여기에서는 아무것도 표시하지 않도록 공백을 지정한다
login_manager.login_message = ""


# create_app 함수를 작성한다
def create_app(config_key):
    
    # Flask 인스턴스 생성
    app = Flask(__name__)
    app.config.from_object(config[config_key])
    
    # app.config.from_mapping(
    #     SECRET_KEY = "2AZSMss3p5QPbcY2hBsJ",
    #     SQLALCHEMY_DATABASE_URI=
    #     f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
    #     #ORACLE : "oracle://사용자ID:PWD@localhost:1521:XE"
    #     SQLALCHEMY_TRACK_MODIFICATIONS=False,
    #     SQLALCHEMY_ECHO=True,
    #     WTF_CSRF_SECRET_KEY="ajkhefkshSEFesfkjjes"
    # )
    
    csrf.init_app(app)
    
    # SQLAlchemy와 앱을 연계한다
    db.init_app(app)
    # Migrate와 앱을 연계한다
    Migrate(app, db)
    # login_manager를 애플리케이션과 연계한다
    login_manager.init_app(app)
    
    
    # crud 패키지로부터 views를 import한다
    from apps.crud import views as crud_views
    
    # register_blueprint를 사용해 views의 crud를 앱에 등록한다
    app.register_blueprint(crud_views.crud, url_prefix="/crud")
    
    # 이제부터 작성하는 auth 패키지로부터 views를 import한다
    from apps.auth import views as auth_views

    # register_blueprint를 사용해 views의 auth를 앱에 등록한다
    app.register_blueprint(auth_views.auth, url_prefix="/auth")
    
    
    # 이제부터 작성하는 detector 패키지로부터 views를 import한다
    from apps.detector import views as dt_views

    # register_blueprint를 사용해 views의 dt를 앱에 등록한다
    app.register_blueprint(dt_views.dt)
    
    from apps.notice import views as notice_views

    # register_blueprint를 사용해 views의 dt를 앱에 등록한다
    app.register_blueprint(notice_views.notice, url_prefix="/notice")
    
    # 커스텀 오류 화면을 등록한다
    app.register_error_handler(404, page_not_found)
    # app.register_error_handler(Exception, internal_server_error)
    
    
    return app


def page_not_found(e):
    return render_template("404.html"),404
    
def internal_server_error(e):
    return render_template("500.html"),500

