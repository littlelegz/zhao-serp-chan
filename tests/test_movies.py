import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    ("query", "message"), 
    (
        ("", b"This field is required."),
        ("s", b"Too many results"),
        ("house in sand and fog", b"Movie not found"),
        ('a' * 101, b"Field must be between 1 and 100 characters long.")
    )
)
def test_search_input_validation(client, query, message):
    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert message in response.data


def test_movie_review(client, auth):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200 

    auth.register()
    auth.login()

    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(10))

    review = SimpleNamespace(text=random_string, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post("/movies/tt2015381", data=form.data, follow_redirects=True)

    assert str.encode(random_string) in response.data
    comment = Review.objects(content=random_string).first()
    assert comment is not None
    



@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("", 404),
        ("abc", 302),
        ("tt201538a", 302),
        ("aaaaaaaaa", 302),
    )
)
def test_movie_review_redirects(client, movie_id, message):
    resp = client.get(f"/movies/{movie_id}")

    assert resp.status_code == message


@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("", b"This field is required"),
        ("a", b"Field must be between 5 and 500 characters long."),
        ('a'*501, b"Field must be between 5 and 500 characters long.")
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    auth.register()
    auth.login()
    
    review = SimpleNamespace(text=comment, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    response = client.post("/movies/tt2015381", data=form.data, follow_redirects=True)
    assert message in response.data

