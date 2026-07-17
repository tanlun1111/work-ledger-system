import os
from flask import current_app
from app import db
from app.models.ledger_image import LedgerImage
from app.utils import upload as upload_utils


def upload_images(ledger_id, files):
    uploaded = []
    saved_names = []

    if not files:
        return uploaded

    for file in files:
        if not file or not file.filename:
            continue

        safe_name, tmp_path = upload_utils.save_to_tmp(file)
        size = os.path.getsize(tmp_path)
        mime_type = file.content_type

        try:
            image = LedgerImage(
                ledger_id=ledger_id,
                uuid_filename=safe_name,
                original_name=file.filename,
                file_size=size,
                mime_type=mime_type,
            )
            db.session.add(image)
            db.session.flush()

            upload_utils.move_from_tmp(safe_name)
            saved_names.append(safe_name)

            uploaded.append({
                "id": image.id,
                "uuid_filename": image.uuid_filename,
                "original_name": image.original_name,
                "file_size": image.file_size,
            })
        except Exception:
            upload_utils.cleanup_tmp(safe_name)
            db.session.rollback()
            raise

    db.session.commit()
    return uploaded


def delete_image(ledger_id, image_id):
    image = LedgerImage.query.filter_by(id=image_id, ledger_id=ledger_id).first()
    if not image:
        raise FileNotFoundError("图片不存在")

    safe_name = image.uuid_filename
    db.session.delete(image)
    db.session.commit()

    upload_utils.delete_file(safe_name)


def get_image_path(ledger_id, uuid_filename):
    image = LedgerImage.query.filter_by(ledger_id=ledger_id, uuid_filename=uuid_filename).first()
    if not image:
        raise FileNotFoundError("图片不存在")

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], uuid_filename
    )

    if not os.path.exists(file_path):
        tmp_path = os.path.join(
            current_app.config["UPLOAD_TMP_FOLDER"], uuid_filename
        )
        if os.path.exists(tmp_path):
            file_path = tmp_path
        else:
            raise FileNotFoundError("图片文件不存在")

    return file_path, image.mime_type
