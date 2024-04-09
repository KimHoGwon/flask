import uuid
from pathlib import Path

import random
import cv2
import numpy as np
import torch
import torchvision
import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app
)

from flask_login import current_user, login_required

from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage,UserImageTag
from apps.detector.forms import UploadImageForm,DetectorForm,DeleteForm

dt = Blueprint("detector", __name__, template_folder="templates")


@dt.route('/')
def index():
    return render_template('detector/main.html')


@dt.route("/dindex")
def dindex():
    
    user_images,user_image_tag_dict = get_user_images()
    
    detector_form = DetectorForm()
    
    delete_form = DeleteForm()
    
    return render_template("detector/index.html",
                           user_images=user_images,
                           detector_form=detector_form,
                           delete_form=delete_form,
                           user_image_tag_dict=user_image_tag_dict,
                           )


@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@dt.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        file = form.image.data
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        user_image = UserImage(user_id=current_user.id, image_path=image_uuid_file_name)
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.dindex"))
  
    return render_template("detector/upload.html", form=form)


def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color


def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line


def draw_lines(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2    


def draw_texts(result_image, line, c1, cv2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [225, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2


def exec_detect(target_image_path):
    labels = current_app.config["LABELS"]
    image = Image.open(target_image_path)
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    model = model.eval()
    
    output = model([image_tensor])[0]
    tags = []
    result_image = np.array(image.copy())
    
    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.5 and labels[label] not in tags:
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            cv2 = draw_lines(c1, c2, result_image, line, color)
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])

    detected_image_file_name = str(uuid.uuid4()) + ".jpg"  
    detected_image_file_path = str(
        Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )  
    
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return tags, detected_image_file_name


def save_detected_image_tags(user_image, tags, detected_image_file_name):
    user_image.image_path = detected_image_file_name
    user_image.is_detected = True
    db.session.add(user_image)
   
    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
    
    db.session.commit()
    

@dt.route("/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        flash("물체 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.dindex"))

    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)
    
    tags, detected_image_file_name = exec_detect(target_image_path)
    
    try:
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except Exception as e:
        flash("물체 검지 처리에서 오류가 발생했습니다. ")
        db.session.rollback()
        current_app.logger.error(e)
        return redirect(url_for("detector.dindex"))
    
    return redirect(url_for("detector.dindex"))


@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)
   
    if os.path.isfile(target_image_path):
        os.remove(target_image_path)
        
    try:
        db.session.query(UserImageTag).filter(UserImageTag.user_image_id == image_id).delete()
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        
    return redirect(url_for("detector.dindex"))



@dt.route("/images/search", methods=["GET"])
def search():
    page_url = "detector/index.html"
    
    search_text = request.args.get("search")

    user_images,user_image_tag_dict = get_user_images(
        user_id=current_user.id,
        user_search_tag_text=search_text
        )

    delete_form = DeleteForm()
    detector_form = DetectorForm()

    return render_template(page_url,
                           user_images=user_images,
                           detector_form=detector_form,
                           delete_form=delete_form,
                           user_image_tag_dict=user_image_tag_dict,
                           )
    

def get_user_images(user_id="",user_search_tag_text="", is_tag=False):
    user_image_tag_dict = {}
    
    user_images = (
        db.session.query(User,UserImage)
        .join(User,UserImage.user_id == User.id)
    )
    if is_tag:
        user_images = user_images.join(UserImageTag,UserImageTag.user_image_id == UserImage.id)
    
    if user_id:
        user_images = user_images .filter(User.id==current_user.id)
    if user_search_tag_text:
        user_images = user_images.filter(UserImageTag.tag_name.like("%"+user_search_tag_text+"%"))
        
    user_images=user_images.all()
    
    for user_image in user_images:
   
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags
    
    return [user_images,user_image_tag_dict]

@dt.errorhandler(404)
def page_not_found(e):
    return render_template("detector/404.html"), 404
