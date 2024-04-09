from apps.app import db
from apps.crud.models import User
from apps.crud.forms import UserForm

from werkzeug.security import check_password_hash

from flask import Blueprint,render_template, redirect, url_for, request, flash

from flask_login import login_required



# Blueprint로 crud 앱을 생성한다
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)




# index 엔드포인트를 작성하고 index.html을 반환한다
@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")


@crud.route("/sql")
@login_required
def sql():
    #SELECT
    user = db.session.query(User).filter_by(id=1).all()
    print(user)
    
    # user=User(
    #     username="사용자명",
    #     email="flaskbook@example.com",
    #     password="비밀번호"
    # )
    #db.session.add(user)
    #db.session.commit()
    
    #UPDATE
    # user = db.session.query(User).filter_by(id=1).first()
    # #print(user.email)
    # user.username="사용자명2"
    # user.email="flaskbook2@name.com"
    # user.password="12233445"
    
    # db.session.add(user)
    # db.session.commit()
    
    
    #Delete
    # user=db.session.query(User).filter_by(id=1).delete()
    # db.session.commit()
    
    
    return "콘솔 로그를 확인해 주세요"

@crud.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    # UserForm을 인스턴스화한다
    form = UserForm()

    # 폼의 값을 벨리데이트한다
    if form.validate_on_submit():
        # 사용자를 작성한다
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # 사용자를 추가하고 커밋한다
        db.session.add(user)
        db.session.commit()

        # 사용자의 일람 화면으로 리다이렉트한다
        return redirect(url_for("crud.users"))
    #return render_template("crud/create.html", form=form)
    return render_template("crud/create_html.html", form=form)


@crud.route("/users/new/html", methods=["GET","POST"])
@login_required
def create_user_html():
    
    if request.method == "POST":
        user = User(
            #queryString : ?key=value&key=value.......
            
            #username=request.args.get("username"),
            #email=request.args.get("email"),
            #password=request.args.get("password")
            
            #<form> 입력
            username = request.form["username"],
            email = request.form["email"],
            password = request.form["password"]
        )    
        
        # 사용자를 추가하고 커밋한다
        print("username : ",user.username)
        print("email : ",user.email)
        print("password : ",user.password_hash)
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("crud.users"))
    
    return render_template("crud/create_html.html")

@crud.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("crud/index.html", users=users)


# methods에 GET과 POST를 지정한다
@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    form = UserForm()
    # User 모델을 이용하여 사용자를 취득한다
    user = User.query.filter_by(id=user_id).first()
    
    if request.method == "POST":
        
        #insert user
        # user = User(
        #     username = request.form["username"], 
        #     password = request.form["password"],
        #     email = request.form["email"]
        # )

        #update
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.password = request.form["password"]
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("crud.users"))
        
    # GET의 경우는 HTML을 반환한다
    return render_template("crud/edit_html.html", user=user, form=form)




#패스워드 변경
from flask import render_template, flash, redirect, url_for, request
from apps.crud.forms import PasswordCheckForm  # 모듈 import 변경

@crud.route("/pwd_check", methods=["GET", "POST"])
@login_required
def pwd_check():
    id = request.args.get("id")
    form = PasswordCheckForm(user_id=id)  # PasswordCheckForm 사용 변경

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data

        user = db.session.query(User).filter_by(id=user_id).first()

        if user and check_password_hash(user.password_hash, password):
            return render_template("crud/pwd_change.html")
        else:
            flash("패스워드가 일치하지 않습니다.")

    return render_template("crud/pwd_check.html", form=form, id=id)

@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        flash('해당 유저를 찾을 수 없습니다.','error')
    return redirect(url_for('crud.users'))