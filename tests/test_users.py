from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/users/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/users/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(("username", "password", "message"), 
(
    ("", "password", b"This field is required"),
    ("username", "", b"This field is required"),
    ("test", "test1", b"Login failed. Check your username and/or password"),
    ("test1", "test", b"Login failed. Check your username and/or password")
)
)
def test_login_input_validation(auth, username, password, message):
    auth.register()
    response = auth.login(username=username, password=password)

    assert message in response.data


def test_logout(client, auth):
    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"

    response = auth.logout()

    assert response.status_code == 302



def test_change_username(client, auth):
    auth.register()
    auth.login()
    review = SimpleNamespace(username="test1", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=review)
    client.post("/users/account", data=form.data, follow_redirects=True)
    response = auth.login(username="test1", password="test")
    assert b"Hey, test1" in response.data

    user = User.objects(username="test1").first()

    assert user is not None




def test_change_username_taken(client, auth):
    auth.register()
    auth.register(username="test1", email="email1@email.com",passwrd="test",confirm="test")
    auth.login()

    review = SimpleNamespace(username="test1", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=review)
    response = client.post("/users/account", data=form.data, follow_redirects=True)

    assert b"That username is already taken" in response.data

@pytest.mark.parametrize(
    ("new_username","message"), 
    (
        ("", b"This field is required."),
        ('a'*41, b"Field must be between 1 and 40 characters long.")
    )
)
def test_change_username_input_validation(client, auth, new_username, message):
    auth.register()
    auth.login()

    review = SimpleNamespace(username=new_username, submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=review)
    response = client.post("/users/account", data=form.data, follow_redirects=True)

    assert message in response.data