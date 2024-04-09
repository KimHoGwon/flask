from flask import Blueprint, render_template, redirect, url_for, flash, request
from apps.notice.form import NoticeForm
from apps.notice.models import Notice
from datetime import datetime
from flask_login import current_user
from apps.app import db


notice = Blueprint('notice', __name__, template_folder="templates")

@notice.route('/create', methods=['GET', 'POST'])
def create_notice():
    form = NoticeForm()
   
    if form.validate_on_submit():
        author = current_user.username if current_user.is_authenticated else "Anonymous"
        notice = Notice(
            title=form.title.data,
            author=author,
            content=form.content.data
        )
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for('notice.notice_index'))
   
       
    return render_template('notice/create.html', title='새로운 공지사항 작성', form=form)

@notice.route('/index')
def notice_index():
    notices = Notice.query.all()
    user = current_user
    notices.reverse()  
    return render_template('notice/index.html', title='공지사항 일람', notices=notices, user=user)

@notice.route('/detail/<int:notice_id>')
def notice_detail(notice_id):
    notice = Notice.query.filter_by(id=notice_id).first()

    return render_template('notice/detail.html', notice=notice)


    
@notice.route('/edit/<int:notice_id>', methods=['GET', 'POST'])
def edit_notice(notice_id):
    notice = Notice.query.get(notice_id)
    form = NoticeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            notice.title = form.title.data
            notice.content = form.content.data
            db.session.commit()
            return redirect(url_for('notice.notice_detail', notice_id=notice.id))
    elif request.method == 'GET':
        form.title.data = notice.title
        form.content.data = notice.content
    return render_template('notice/edit.html', title='공지사항 수정', form=form, notice=notice)

@notice.route('/delete/<int:notice_id>', methods=['GET'])
def delete_notice(notice_id):
    notice = Notice.query.get(notice_id)
    if notice:
        db.session.delete(notice)
        db.session.commit()
    else:
        flash('해당 공지사항을 찾을 수 없습니다.', 'error')
    return redirect(url_for('notice.notice_index'))
