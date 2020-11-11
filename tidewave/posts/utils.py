import os
import secrets
from PIL import Image
from flask import url_for, current_app


# These functions are used to process uploaded images and save them correctly

def save_logo(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/project_logos', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    output_size = (600, 400)
    try:
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn
    except:
        return False
