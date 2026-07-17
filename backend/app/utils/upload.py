import uuid
import os
from flask import current_app

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_extension(filename):
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def generate_uuid_filename(original_name):
    ext = get_extension(original_name)
    if not ext:
        ext = "jpg"
    return f"{uuid.uuid4().hex}.{ext}"


def validate_image(file):
    if not file or not file.filename:
        raise ValueError("未选择文件")

    if file.content_type not in current_app.config["ALLOWED_IMAGE_TYPES"]:
        raise ValueError(f"不支持的文件类型: {file.content_type}")

    if not allowed_file(file.filename):
        raise ValueError(f"不支持的文件扩展名")

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > current_app.config["SINGLE_IMAGE_MAX_SIZE"]:
        raise ValueError(f"文件大小不能超过 10MB")
    if size == 0:
        raise ValueError("文件为空")

    return size


def save_to_tmp(file):
    validate_image(file)
    safe_name = generate_uuid_filename(file.filename)
    tmp_path = os.path.join(current_app.config["UPLOAD_TMP_FOLDER"], safe_name)
    file.save(tmp_path)
    return safe_name, tmp_path


def move_from_tmp(safe_name):
    tmp_path = os.path.join(current_app.config["UPLOAD_TMP_FOLDER"], safe_name)
    dest_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
    if not os.path.exists(tmp_path):
        raise FileNotFoundError(f"临时文件不存在: {safe_name}")
    os.rename(tmp_path, dest_path)
    return dest_path


def delete_file(safe_name):
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
    if os.path.exists(file_path):
        os.remove(file_path)


def cleanup_tmp(safe_name):
    tmp_path = os.path.join(current_app.config["UPLOAD_TMP_FOLDER"], safe_name)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
