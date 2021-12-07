from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from random import randint
from .. import pic_client
from ..forms import MovieReviewForm, SearchForm, PostForm, CommentForm
from ..models import User, Review, Post
from ..utils import current_time

movies = Blueprint('movies', __name__)

@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    posts = Post.objects(comment_on=None).order_by('-post_id')
    if posts.count() > 20:
        posts = posts[:20]

    return render_template("index.html", posts=posts, form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        posts = Post.objects(content__contains=query).order_by('-post_id')
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("movies.index"))

    return render_template("query.html", posts=posts, query=query)

@movies.route("/reply/<input_id>", methods=["GET", "POST"])
def reply(input_id):
    form = CommentForm()
    if form.validate_on_submit():
        posts = Post.objects()
        count = 0
        for post in posts:
            count += 1
        unique_id = count+1
        if current_user.is_authenticated:
            post = Post(
                anon=None,
                commenter=current_user._get_current_object(),
                content=form.text.data,
                query=None,
                date=current_time(),
                post_id=unique_id,
                comment_on=input_id
            )

            post.save()
        else:
            post = Post(
                anon='Anon',
                content=form.text.data,
                query=None,
                date=current_time(),
                post_id=unique_id,
                comment_on=input_id
            )

            post.save()

        return redirect(url_for("movies.thread", input_id=input_id))

    return render_template(
        "reply.html", form=form
    )

@movies.route("/thread/<input_id>", methods=["GET", "POST"])
def thread(input_id):
    thread_post = Post.objects(post_id=input_id).first()
    comments = Post.objects(comment_on=input_id)

    return render_template(
        "thread.html", thread=thread_post, comments=comments
    )

@movies.route("/post", methods=["GET", "POST"])
def post():
    form = PostForm()
    if form.validate_on_submit():
        posts = Post.objects()
        count = 0
        for post in posts:
            count += 1
        unique_id = str(count+1)
        if current_user.is_authenticated:
            if form.pic_query.data:
                post = Post(
                    anon=None,
                    commenter=current_user._get_current_object(),
                    content=form.text.data,
                    query=pic_client.search(form.pic_query.data)[randint(0,99)].thumbnail,
                    date=current_time(),
                    post_id=unique_id
                )
            else:
                post = Post(
                    anon=None,
                    commenter=current_user._get_current_object(),
                    content=form.text.data,
                    query=None,
                    date=current_time(),
                    post_id=unique_id
                )

            post.save()
        else:
            if form.pic_query.data:
                post = Post(
                    anon='Anon',
                    content=form.text.data,
                    query=pic_client.search(form.pic_query.data)[randint(0,99)].thumbnail,
                    date=current_time(),
                    post_id=unique_id
                )
            else:
                post = Post(
                    anon='Anon',
                    content=form.text.data,
                    query=None,
                    date=current_time(),
                    post_id=unique_id
                )

            post.save()

        return redirect(url_for("movies.index"))

    return render_template(
        "post.html", form=form
    )

@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = pic_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = MovieReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            imdb_id=movie_id, 
            movie_title=result.title,
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    return render_template(
        "movie_detail.html", form=form, movie=result, reviews=reviews
    )


@movies.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    posts = Post.objects(commenter=user, comment_on=None)
    comments = Post.objects(commenter=user, comment_on__exists=True)

    return render_template("user_detail.html", username=username, posts=posts, comments=comments)

@movies.route("/about")
def about():
    return render_template("about.html")


