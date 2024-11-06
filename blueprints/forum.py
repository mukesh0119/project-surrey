from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from helpers import get_user

# Define the blueprint for the forum module
forum_bp = Blueprint('forum', __name__)

# Sample data for users and posts
users = [
    {"id": 1, "username": "john_doe", "email": "john@example.com", "role": "Student"},
    {"id": 2, "username": "jane_smith", "email": "jane@example.com", "role": "Lecturer"}
]

posts = [
    {"id": 1, "title": "Sample Post 1", "content": "This is the first sample post.", "user_id": 1, "comments": [], "category": "General"},
    {"id": 2, "title": "Sample Post 2", "content": "This is the second sample post.", "user_id": 2, "comments": [
        {"content": "This is a comment on post 2", "user_id": 1}
    ], "category": "Academic"}
]


@forum_bp.route('/forum')
def forum():
    if 'logged_in' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
    logged_in_user = get_user(session.get('user_id'), users)
    return render_template('forum.html', posts=posts, users=users, get_user=get_user, logged_in_user=logged_in_user)


@forum_bp.route('/popular_posts')
def popular_posts():
    # Check if the user is logged in
    if 'logged_in' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login.login'))
    
    # Sort posts by the number of comments in descending order
    sorted_posts = sorted(posts, key=lambda post: len(post['comments']), reverse=True)
    logged_in_user = get_user(session.get('user_id'), users)
    return render_template('forum.html', posts=sorted_posts, users=users, logged_in_user=logged_in_user, get_user=get_user)

@forum_bp.route('/create_post', methods=['POST'])
def create_post():
    # Check if the user is logged in
    if 'user_id' in session:
        # Create a new post with data from the form
        new_post = {
            "id": len(posts) + 1,
            "title": request.form['title'],
            "content": request.form['content'],
            "user_id": session['user_id'],
            "comments": [],
            "category": request.form['category']
        }
        posts.append(new_post)
        flash("Post created successfully.")
    return redirect(url_for('forum.forum'))

@forum_bp.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    # Check if the user is logged in
    if 'user_id' in session:
        # Find the post and add a comment
        for post in posts:
            if post['id'] == post_id:
                post['comments'].append({"content": request.form['content'], "user_id": session['user_id']})
                flash("Comment added successfully.")
                break
    return redirect(url_for('forum.forum'))

@forum_bp.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    # Check if the user is logged in
    if 'user_id' in session:
        # Find and delete the post if the user is the owner
        for post in posts:
            if post['id'] == post_id and post['user_id'] == session['user_id']:
                posts.remove(post)
                flash("Post deleted successfully.")
                break
    return redirect(url_for('forum.forum'))
