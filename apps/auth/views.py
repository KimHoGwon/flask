from flask import (
    Blueprint, 
    flash, 
    redirect, 
    render_template, 
    request, 
    url_for
)
from flask_login import login_user,logout_user
from apps.app import db
from apps.crud.models import User

from apps.auth.forms import LoginForm, SignUpForm

auth = Blueprint("auth", 
                 __name__, 
                 template_folder="templates", 
                 static_folder="static"
                 )

@auth.route("/")
def index():
    return render_template("auth/index.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
    
        if user.is_duplicate_email():
            flash("지정한 이메일 주소는 이미 등록되어 있습니다.")
            return redirect(url_for("auth.signup"))

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("crud.users"))

    return render_template("auth/signup.html",form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():

    next_ = request.args.get("next")
    
    form = LoginForm()
    
    if request.method=="POST":
        user = User.query.filter_by(email=form.email.data).first()
        next_ = request.form["next"]
        
        if user is not None and user.verify_password(form.password.data):
        
            login_user(user)
            if next_ is None or not next_.startswith("/"):
                next_ = url_for("detector.index")
            return redirect(next_)
        else:
            flash("메일 주소 또는 비밀번호가 일치하지 않습니다")
            return redirect(url_for("auth.login",next=next_))

    return render_template("auth/login.html",form=form,next = next_)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
