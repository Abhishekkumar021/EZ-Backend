from datetime import datetime
from flask import request, jsonify, current_app, send_file
from app import app, db
import os
from app.models import User, File, OpUser, downloadFile
from app.utils import (
    send_verification_email,
    generate_verification_token,
    encrypt,
)
from werkzeug.utils import secure_filename
import uuid


# for the Normal User Signup


@app.route("/api/signup", methods=["POST"])
def user_signup():
    try:
        data = request.get_json()
        print(f"data : {data}")
        email = encrypt(data.get("email"))
        password = encrypt(data.get("password"))
        name = data.get("name")
        sendMail = data.get("email")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400

        token = generate_verification_token()
        new_user = User(
            name=name,
            email=email,
            password=password,
            verification_token=token,
            token_timestamp=datetime.utcnow(),
        )
        db.session.add(new_user)
        db.session.commit()

        print("***********  Succeess  *********************")
        send_verification_email(new_user, sendMail)

        return (
            jsonify(
                {
                    "message": "User registered successfully. Check your email for verification instructions."
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


# for the Operational User Signup


@app.route("/api/operations/signup", methods=["POST"])
def operations_user_signup():
    try:
        data = request.get_json()
        # print(f"data : {data}")
        email = encrypt(data.get("email"))
        password = encrypt(data.get("password"))
        name = data.get("name")
        sendMail = data.get("email")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = OpUser.query.filter_by(email=email).first()

        if existing_user:
            return (
                jsonify({"error": "Operational User with this email already exists"}),
                400,
            )

        token = generate_verification_token()
        new_user = OpUser(
            name=name,
            email=email,
            password=password,
            verification_token=token,
            token_timestamp=datetime.utcnow(),
        )
        db.session.add(new_user)
        db.session.commit()

        send_verification_email(new_user, sendMail)

        return (
            jsonify(
                {
                    "message": "Operational User registered successfully. Check your email for verification instructions."
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


# for the Operational User login


@app.route("/api/operations/login", methods=["POST"])
def operations_user_login():
    try:
        data = request.get_json()
        # print(f"data : {data}")
        email = encrypt(data.get("email"))
        password = encrypt(data.get("password"))

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = OpUser.query.filter_by(email=email).first()

        if not existing_user or not existing_user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({"message": "Operational User logged in successfully"}), 200

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


# for the Normal User login


@app.route("/api/login", methods=["POST"])
def user_login():
    try:
        data = request.get_json()
        print(f"data : {data}")
        email = encrypt(data.get("email"))
        password = encrypt(data.get("password"))

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user or not existing_user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({"message": "User logged in successfully"}), 200

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_upload_folder():
    parent_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )
    upload_folder = os.path.join(parent_directory, "upload")

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        create_upload_folder()

        email = request.form.get("email")
        # data = request.get_json()
        email = encrypt(
            email
        )  # just for testing else from the frontend request they will send userid as encrypted form from session or local storage

        print(f"email : {email}")
        existing_user = OpUser.query.filter_by(email=email).first()

        if not existing_user:
            return jsonify({"error": "You do not have rights to upload file"}), 401

        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config["UPLOAD_FOLDER"]

            print(
                f"***********  upload_folder url : {upload_folder}  **********************"
            )

            file_path = os.path.join(upload_folder, filename)

            file_path = file_path.replace("\\", "/")

            print(f"***********  file_path url : {file_path}  **********************")

            file.save(file_path)

            existing_file = File.query.filter_by(
                filename=filename, file_path=file_path
            ).first()

            if existing_file:
                return jsonify({"error": "File already exists"}), 400

            file_id = str(uuid.uuid4())

            new_file = File(
                file_id=file_id,
                filename=filename,
                filetype=file.content_type,
                file_path=file_path,
            )
            db.session.add(new_file)
            db.session.commit()

            return jsonify({"message": "File uploaded successfully"}), 201
        else:
            return (
                jsonify(
                    {"error": "Invalid file type. Allowed types are pptx, docx, xlsx"}
                ),
                400,
            )

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


@app.route("/api/verify/<user>/<token>", methods=["GET"])
def verify(user, token):
    try:
        existing_user = User.query.filter_by(email=user).first()
        existing_operational_user = OpUser.query.filter_by(email=user).first()

        if (existing_user.is_token_expired() and existing_user.verified == False) or (
            existing_operational_user.is_token_expired()
            and existing_operational_user.verified == False
        ):
            return jsonify({"error": "Session Expired"}), 404

        if (
            existing_user.verification_token == token
            or existing_operational_user.verification_token == token
        ):
            existing_user.verified = True
            return jsonify({"msg": "Successfully Verified your email"}), 200

        return jsonify({"error": "Something Went wrong! try again later"}), 500

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


@app.route("/api/download/<file_id>", methods=["GET"])
def download(file_id):
    try:
        file = File.query.get(file_id)

        if not file:
            return jsonify({"error": "File not found"}), 404

        full_file_path = os.path.join(
            os.getcwd(), file.file_path.replace("/", os.path.sep)
        )

        print(f"file.file_path.replace : {full_file_path}")

        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404

        token = generate_verification_token()
        url = f"/api/download-file/{token}"

        new_user_file = downloadFile(
            file_token=token,
            file_url=full_file_path,
            token_timestamp=datetime.utcnow(),
        )
        db.session.add(new_user_file)
        db.session.commit()

        # return send_file(full_file_path, as_attachment=True)
        return jsonify({"download-link": url, "Message": "Success"})

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


@app.route("/api/download-file/<token>", methods=["GET"])
def download_file(token):
    try:
        existing_token = downloadFile.query.filter_by(file_token=token).first()

        if not existing_token or existing_token.is_token_expired():
            return jsonify({"error": "Token not found"}), 404

        full_file_path = existing_token.file_url

        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(full_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error ": str(e)}), 500


@app.route("/api/list_files", methods=["GET"])
def list_files():
    try:
        files = []
        database_files = File.query.all()
        for db_file in database_files:
            files.append(
                {
                    "file_id": db_file.file_id,
                    "filename": db_file.filename,
                    "filetype": db_file.filetype,
                    "file_path": db_file.file_path.replace("\\", "/"),
                }
            )

        return jsonify({"files": files})

    except Exception as e:
        return jsonify({"error ": str(e)}), 500
