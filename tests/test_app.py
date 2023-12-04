import unittest
from flask import Flask
from flask_testing import TestCase
from app import app, db
from app.models import User, OpUser, File, downloadFile
from datetime import datetime, timedelta
from app.config import TestConfig


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestAuthRoutes(BaseTestCase):
    def test_user_signup(self):
        response = self.client.post(
            "/api/signup",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", str(response.data))

    def test_user_login(self):
        self.client.post(
            "/api/signup",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "pass12@",
            },
        )
        response = self.client.post(
            "/api/login", json={"email": "john@example.com", "password": "pass12@"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("User logged in successfully", str(response.data))


class TestFileRoutes(BaseTestCase):
    def test_upload_file(self):
        self.client.post(
            "/api/signup",
            json={
                "name": "Operations User",
                "email": "opuser@example.com",
                "password": "pass12@",
            },
        )
        response = self.client.post(
            "/api/operations/login",
            json={"email": "opuser@example.com", "password": "pass12@"},
        )
        self.assertEqual(response.status_code, 200)

        with self.client:
            response = self.client.post(
                "/api/upload",
                data={"email": "opuser@example.com"},
                files={"file": ("test_file.docs", b"Test file content")},
            )
            self.assertEqual(response.status_code, 201)
            self.assertIn("File uploaded successfully", str(response.data))

    def test_list_files(self):
        file = File(
            file_id="1",
            filename="test_file.txt",
            filetype="text/plain",
            file_path="/path/to/file",
        )
        db.session.add(file)
        db.session.commit()

        response = self.client.get("/api/list_files")
        self.assertEqual(response.status_code, 200)
        self.assertIn("test_file.txt", str(response.data))


if __name__ == "__main__":
    unittest.main()
