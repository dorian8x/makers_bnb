import os
from flask import Flask, request, render_template, redirect, flash, jsonify, url_for, session
from lib.database_connection import get_flask_database_connection
from lib.space import Space
from lib.space_repository import SpaceRepository
from lib.user_repository import UserRepository
from lib.user import User
from lib.booking import Booking
from lib.booking_repository import BookingRepository

# from datetime import datetime


# Create a new Flask app
app = Flask(__name__)
app.secret_key = 'the_secret_key' # Does not need to be strong for this project, flask needs this to 'securely' sign cookies

# == Your Routes Here ==

# GET /home
# Returns the homepage
# Try it:
#   ; open http://localhost:5001/home
@app.route('/home', methods=['GET'])
def get_home():
    connection = get_flask_database_connection(app)
    repository = SpaceRepository(connection)
    space_list = repository.all()
    return render_template('home.html', spaces = space_list)


# open sign up page
@app.route('/signup')
def sign_up():
    return render_template("sign_up.html")


# submit sign up info
@app.route('/signup', methods = ['POST'])
def sign_up_form():
    connection = get_flask_database_connection(app)
    repo = UserRepository(connection)

    # check validation
    if not has_valid_data(request.form, connection):
            return "error: inputs not valid", 400

    # read form data to generate new record for "users" table
    save_username = request.form.get('username')
    save_user_password = request.form.get('user_password')
    save_email = request.form.get('email')
    save_full_name = request.form.get('full_name')
    
    new_user = User(None, save_username, save_user_password, save_email, save_full_name)
    repo.add_user(new_user)

    return redirect(url_for("get_home"))


# Route for logging in as a user
# Once logged in you can show logged in users different versions of a page by adding an if statement to check whether a user session exists:
"""
if 'username' in session:
    connection = get_flask_database_connection(app)
    repository = SpaceRepository(connection)
    space_list = repository.all()
    return render_template('home.html', spaces = space_list, username=session['username'])
else:
    return redirect(url_for('login')) """
# In the above example if a user session exists the user can access home, if the user is not logged in they are redirected to the login page
@app.route('/loginpage', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['user_password']
        connection = get_flask_database_connection(app)
        repo = UserRepository(connection)
        user = repo.find_by_username(username)
        if user and user.user_password == password:
            session['user_id'] = user.id
            session['username'] = username
            return redirect(url_for('get_home'))
        else:
            flash('Invalid username or password')  # It's better to use flash messages for errors
            return redirect(url_for('loginpage'))
    return render_template('loginpage.html')


# Route for logging out of a user session
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/requests', methods = ['GET'])
def get_requests():
    connection = get_flask_database_connection(app)
    id = session['user_id']
    requests_as_guest = connection.execute(
        "SELECT * FROM bookings JOIN spaces "\
        "ON bookings.space_id = spaces.id "\
        "WHERE guest_id = %s",
        [id]
        )
    requests_as_host = connection.execute(
        "SELECT * FROM bookings JOIN spaces "\
        "ON bookings.space_id = spaces.id "\
        "WHERE bookings.host_id = %s",
        [id]
        )
    return render_template(
        "requests.html",
        requests_as_guest=requests_as_guest,
        requests_as_host=requests_as_host,
        id=id
        )


@app.route('/request/<booking_id>', methods = ['GET'])
def check_request(booking_id):
    if "username" not in session:
        return redirect(url_for('login'))
    connection = get_flask_database_connection(app)
    booking_repo = BookingRepository(connection)
    booking = booking_repo.find(booking_id)
    space_repo = SpaceRepository(connection)
    space = space_repo.find_space(booking.space_id)
    guest_repo = UserRepository(connection)
    guest = guest_repo.find_user_by_id(booking.guest_id)
    other_requests = booking_repo.find_by_space_id(booking.space_id)
    return render_template(
        "request.html",
        booking=booking,
        space=space,
        guest=guest,
        other_requests=other_requests
        )


@app.route("/request/<booking_id>", methods = ['POST'])
def decide_request(booking_id):
    connection = get_flask_database_connection(app)
    booking_repo = BookingRepository(connection)
    booking = booking_repo.find(booking_id)
    # confirm = request.form.get("confirm")
    # deny = request.form.get("deny")
    user_id = session['user_id']
    date = booking.booking_date
    space_id  = booking.space_id
    if request.form["booking_status"] == "approved":
        booking_repo.update(booking_id, "approved")
        connection.execute(
            "UPDATE bookings SET booking_status='denied' "\
            "WHERE id != %s AND booking_date = %s "\
            "AND host_id = %s AND space_id = %s",
            [booking_id, date, user_id, space_id]
            )
        return redirect(url_for('get_requests'))
    if request.form["booking_status"] == "denied":
        booking_repo.update(booking_id, "denied")
        return redirect(url_for('get_requests'))


def has_valid_data(form, connection):
    handle = form['username']
    email = form['email']
    password = form['user_password']
    repo = connection.execute("SELECT * FROM users WHERE username = %s OR email = %s", [handle, email])

    if repo != []:
        return handle not in repo[0]['username'] and \
            email not in repo[0]['email'] and \
            len(password) >= 8 and \
            any(char in 'qwertyuiopasdfghjklzxcvbnm' for char in password) and \
            any(char in 'QWERTYUIOPASDFGHJKLZXCVBNM,' for char in password) and \
            any(char in '!@£$%^&*//.,' for char in password) and \
            any(char in '1234567890' for char in password)
    return len(password) >= 8 and \
        any(char in 'qwertyuiopasdfghjklzxcvbnm' for char in password) and \
        any(char in 'QWERTYUIOPASDFGHJKLZXCVBNM,' for char in password) and \
        any(char in '!@£$%^&*//.,' for char in password) and \
        any(char in '1234567890' for char in password)


# open sign up page
@app.route('/newlisting')
def new_listing():
    return render_template("newlisting.html")


@app.route("/space/<id>", methods = ["GET"])
def get_space(id):
    connection = get_flask_database_connection(app)
    space_repo = SpaceRepository(connection)
    found_space = space_repo.find_space(id)
    return render_template("space.html", space = found_space)


# submit sign up info
@app.route('/space', methods = ['POST'])
def new_listing_form():
    connection = get_flask_database_connection(app)
    space_repo = SpaceRepository(connection)

    # check validation
    # if not has_valid_data(request.form, connection):
    #         return "error: inputs not valid", 400

    # read form data to generate new record for "spaces" table
    save_address = request.form.get('address')
    save_description = request.form.get('description')
    save_price = request.form.get('price')
    save_user_id = session["user_id"]
    new_space = Space(None, save_address, save_description, save_price, save_user_id)
    space_repo.add(new_space)
    new_space = space_repo.all()[-1]
    return redirect(url_for("get_space", id = f"{new_space.space_id}"))


# These lines start the server if you run this file directly
# They also start the server configured to use the test database
# if started in test mode.
if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5001)))
