from flask import request, redirect, render_template, url_for, flash, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from flask_restful import Resource
from werkzeug.security import check_password_hash, generate_password_hash

from blog import app, manager, api
from blog.db import Session, session
from blog.models import User, Post


@manager.user_loader
def load_user(user_id):
    with Session() as session:
        user = session.query(User).get(user_id)
        return user


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('psw')
    password2 = request.form.get('psw2')

    if request.method == 'POST':
        if not username or not password or not password2:
            flash('Пожалуйста, заполниет все поля!')
        elif password != password2:
            flash('Пароли не совпадают!')
        else:
            with Session() as session:
                psw_hash = generate_password_hash(password)
                new_user = User(username=username, password=psw_hash)
                session.add(new_user)
                session.commit()

                return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('psw')

    if username and password:
        with Session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user and (check_password_hash(user.password, password) or user.is_superuser):
                login_user(user)

                return render_template('index.html')
            else:
                flash('Неверный логин или пароль')
    else:
        flash('Пожалуйста введите логин и пароль')

    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


class PostListResource(Resource):
    @login_required
    def get(self):
        with Session() as session:
            posts_users = session.query(
                User.username,
                Post.title,
                Post.created_at,
                Post.updated_at,
            ).join(
                isouter=False,
                target=Post,
                onclause=User.id == Post.users).all()

            return jsonify(
                {
                    'posts': [
                        {
                            'username': post_user.username,
                            'post_title': post_user.title,
                            'created_at': post_user.created_at,
                            'updated_at': post_user.updated_at
                        }
                        for post_user in posts_users
                    ]
                }
            )

    @login_required
    def post(self):
        if not request.form or 'title' not in request.form:
            abort(400, 'Поле title является обязательным')

        title = request.form.get('title')
        text = request.form.get('text')

        new_post = Post(title=title, text=text, users=current_user.id)

        with Session() as session:
            session.add(new_post)
            session.commit()

        return jsonify({'message': 'Post created successfully'})


class PostResource(Resource):
    @login_required
    def get(self, post_id):
        post = session.get(Post, post_id)

        if not post:
            return jsonify(
                {
                    'message': 'Post not found'
                }
            )

        return jsonify(
            {
                'post': {
                    'title': post.title,
                    'text': post.text,
                    'created_at': post.created_at,
                    'updated_at': post.updated_at,
                    'author': session.get(User, post.users).username
                }
            }
        )

    @login_required
    def put(self, post_id):
        with Session() as session:
            post = session.get(Post, post_id)

            if not post:
                return jsonify(
                    {
                        'error': 'Post not found'
                    }
                )

            if post.users != current_user.id and not current_user.is_superuser:
                abort(403, 'Not permissions')

            new_title = request.form.get('title')
            new_text = request.form.get('text')

            if new_title:
                post.title = new_title
            if new_text:
                post.text = new_text

            session.add(post)
            session.commit()

            return jsonify(
                {
                    'message': 'Post has been updated',
                    'post': {
                        'title': post.title,
                        'text': post.text,
                        'update_at': post.updated_at,
                        'created_at': post.created_at
                    }
                }
            )

    @login_required
    def delete(self, post_id):
        post = session.get(Post, post_id)

        if not post:
            return jsonify(
                {
                    'error': 'Post not found'
                }
            )

        if post.users != current_user.id and not current_user.is_superuser:
            abort(403, 'Not permissions')

        session.delete(post)
        session.commit()

        return jsonify(
            {
                'message': 'Post delete successfully'
            }
        )


class UserListResource(Resource):
    @login_required
    def get(self):
        with Session() as sess:
            users = sess.query(User).all()

            return jsonify(
                {
                    'users': [
                        {
                            'username': user.username,
                            'email': user.email,
                            'is_superuser': user.is_superuser
                        }
                        for user in users
                    ]
                }
            )


class UserResource(Resource):
    @login_required
    def get(self, user_id):
        user = session.get(User, user_id)
        if not user:
            return jsonify(
                {
                    'message': 'user not found'
                }
            )

        return jsonify(
            {
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'is_superuser': user.is_superuser,
                }
            }
        )

    @login_required
    def put(self, user_id):
        user = session.get(User, user_id)

        if user is current_user or current_user.is_superuser:

            if request.form:
                user.username = request.form.get('username', default=user.username)

                try:
                    user.email = request.form.get('email', default=user.email)
                except ValueError:
                    return jsonify(
                        {
                            'message': 'Incorrect email'
                        }
                    )

                user.is_superuser = True if request.form.get('is_superuser') == 'True' else False
                session.commit()

            return jsonify(
                {
                    'message': 'User update successfully'
                }
            )

        return jsonify(
            {
                'message': 'Not permissions'
            }
        )

    @login_required
    def delete(self, user_id):
        user = session.get(User, user_id)

        if not user:
            return jsonify(
                {
                    'message': 'User not found'
                }
            )

        if user.id == current_user.id or current_user.is_superuser:
            session.delete(user)
            session.commit()

            return jsonify(
                {
                    'message': 'User delete successfully'
                }
            )

        return jsonify(
            {
                'message': 'Not permissions'
            }
        )


api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(PostListResource, '/posts')
api.add_resource(PostResource, '/posts/<int:post_id>')
