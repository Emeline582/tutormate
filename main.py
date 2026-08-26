from flask import Flask, render_template,request,redirect,url_for,flash,session
from database import insert_user, get_user, update_user, delete_user, check_user_exists, insert_tutor, get_tutors, get_tutor, update_tutor, delete_tutor,  get_tutor_availability, insert_student, get_student, update_student, delete_student, insert_booking, get_booking, update_booking,  cancel_booking, confirm_booking, complete_booking, get_student_bookings, get_tutor_bookings, insert_payment, get_payments, confirm_payments, get_pending_payments,update_payment ,insert_review, get_review, update_review, delete_review, get_tutor_reviews, insert_availability, get_availability, update_availability, delete_availability,get_available_slots, get_available_tutors, mark_slot_booked, mark_slot_available, insert_notification, get_notification, update_notification, delete_notification, get_user_notifications, mark_as_read, mark_as_unread, count_notifications, send_booking_notification,count_bookings,count_pending_payments,count_students,count_tutors,count_users,count_upcoming_bookings,count_completed_bookings,count_student_pending_payments,count_tutor_bookings,count_tutor_upcoming_bookings,get_tutor_by_user_id,get_student_by_user_id,get_user_by_id,decline_booking,insert_notification_for_student,mark_booking_paid,mark_booking_unpaid,get_student_user_id_from_booking,add_payment_notification,get_all_bookings
from datetime import date, datetime



from flask_bcrypt import Bcrypt
from functools import wraps 

app = Flask(__name__)
app.secret_key = 'Gfghjk'


bcrypt = Bcrypt(app)

@app.route('/')
def home():
    
    return  render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

def login_required(f):
    @wraps(f)
    def protected(*args,**kwargs):
        if 'email' not in session: 
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return protected

def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role')!= 'tutor':
            flash("Only tutors can edit tutor profiles", "error")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone']
        role = request.form['role'].strip().lower()
        password = request.form['password']

        existing_user = check_user_exists(email)

        if not existing_user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = (first_name,last_name,email,phone_number,role,hashed_password)

            insert_user(new_user)

            user = check_user_exists(email)
            user_id = user[0]

            if role == "student":
                insert_student(user_id,"","","","")

            elif role == "tutor":
                insert_tutor(user_id,"", "",0,0.00,"","")

            flash("User created successfully", "success")
            return redirect(url_for('login'))

        else:
            flash("User already exists, please login instead", "danger")

    return render_template('register.html')



@app.route("/profile")
@login_required
def profile():
    user = get_user_by_id(session["user_id"])
    return render_template("profile.html", user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        registered_user = check_user_exists(email)

        if not registered_user:
            flash("User doesn't exist. Please register first.", "danger")
            return redirect(url_for('register'))

        if bcrypt.check_password_hash(registered_user[5], password):
            session['user_id'] = registered_user[0]
            session['email'] = registered_user[3]
            session['role'] = registered_user[6]

            flash("Login successful.", "success")

            if registered_user[6] == "admin":
                return redirect(url_for("admin_dashboard"))

            elif registered_user[6] == "tutor":
                tutor = get_tutor_by_user_id(registered_user[0])
                if tutor:
                    session['tutor_id'] = tutor[0]
                    return redirect(url_for("tutor_dashboard"))
                else:
                    flash("Tutor profile not found.", "danger")
                    return redirect(url_for("login"))

           

            elif registered_user[6] == "student":
                student = get_student_by_user_id(registered_user[0])
                if student:
                    session['student_id'] = student[0]
                    return redirect(url_for("student_dashboard"))
                else:
                    flash("Student profile not found.", "danger")
                    return redirect(url_for("login"))

        else:
            flash("Incorrect password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out")

    return redirect(url_for("login"))





@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash("Please login first.", "danger")
        return redirect(url_for('login'))
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('login'))

    
    try:
        u = count_users()
        t = count_tutors()
        s = count_students()
        b = count_bookings()
        p = count_pending_payments()
        print(f"COUNTS FROM DB: {u}, {t}, {s}, {b}, {p}")
    except Exception as e:
        print(f"COUNT ERROR: {e}")
        u = t = s = b = p = f"ERROR: {e}"

    return render_template('admin_dashboard.html',
                           total_users=u,
                           total_tutors=t,
                           total_students=s,
                           total_bookings=b,
                           pending_payments=p)


@app.route('/student_dashboard')
@login_required
def student_dashboard():

    student_id = session.get('student_id')

    

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    user_id = session.get('user_id')
    user = get_student_by_user_id(user_id)

    return render_template('student_dashboard.html',upcoming_bookings=count_upcoming_bookings(student_id), completed_bookings=count_completed_bookings(student_id), pending_payments=count_student_pending_payments(student_id),   bookings_status=get_student_bookings(student_id) )


@app.route('/tutor_dashboard')
@login_required
def tutor_dashboard():

    tutor_id = session.get('tutor_id')
    user_id = session['user_id']

    if session.get("role") != "tutor":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    return render_template(
        "tutor_dashboard.html",

        total_bookings=count_tutor_bookings(tutor_id),

        upcoming_bookings=count_tutor_upcoming_bookings(tutor_id),


        bookings=get_tutor_bookings(tutor_id),

        reviews=get_tutor_reviews(tutor_id))

@app.route("/tutors")
def tutors():
    tutors = get_tutors()
    return render_template("tutors.html",tutors = tutors)

@app.route('/tutors_profile', methods=['GET', 'POST'])
@login_required
def tutors_profile_r():
    if session.get('role')!= 'tutor':
        flash("Access denied", "danger")
        return redirect(url_for('login'))

    tutor_id = session.get('tutor_id')
    tutor = get_tutor(tutor_id)

    if request.method == 'POST':
        subject = request.form['subject']
        qualification = request.form['qualification']
        experience_years = request.form['experience_years']
        hourly_rate = request.form['hourly_rate']
        bio = request.form['bio']
        availability = request.form['availability']

        update_tutor(tutor_id, subject, qualification, experience_years, hourly_rate, bio, availability)
        flash("Profile updated successfully", "success")
        return redirect(url_for('tutor_dashboard'))

    return render_template('tutors_profile.html', tutor=tutor)

@app.route("/view_tutor/<int:tutor_id>")
@login_required
def view_tutor(tutor_id):

    tutor = get_tutor(tutor_id)

    return render_template("tutors_profile.html", tutor=tutor)

@app.route("/payments")
def payments():
    payments_data = get_payments()
    return render_template("payments.html",payments_data = payments_data)

@app.route("/add_tutor", methods=["GET","POST"])
@login_required
def add_tutor():

    if request.method == "POST":

        insert_tutor(request.form)

        flash("Tutor Added")

        return redirect(url_for("tutors"))

    return render_template("add_tutor.html")

@app.route("/edit_tutor/<int:id>", methods=["GET","POST"])
@login_required
@tutor_required
def edit_tutor(id):

    tutor = get_tutor(id)

    if request.method == "POST":

        update_tutor(id, request.form)

        return redirect(url_for("tutors"))

    return render_template("edit_tutor.html", tutor=tutor)

@app.route("/delete_tutor/<int:id>")
@login_required
def delete_tutor_route(id):

 
    flash("Tutor Deleted")

    return redirect(url_for("tutors"))






@app.route('/book/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
def book_tutor(tutor_id):
    tutor = get_tutor(tutor_id) 

    if request.method == 'POST':
        student_id = session.get('student_id')
        subject = request.form['subject']
        date = request.form['date']
        start = request.form['start_time']
        end = request.form['end_time']

        
        insert_booking(student_id, tutor_id, subject, date, start, end, 'Pending')
        
        flash("Booking successful!", "success")
        return redirect(url_for('my_bookings'))

    return render_template('book_tutor.html', tutor=tutor, tutor_id=tutor_id)
@app.route('/confirm_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def confirm_booking_r(booking_id):
    confirm_booking(booking_id)
    booking = get_booking(booking_id)
    student_id = booking[1] 
    insert_notification_for_student(student_id, "Booking Confirmed", "Your tutoring booking has been confirmed.", "booking", False)
    flash("Booking confirmed successfully.", "success")
    return redirect(url_for('tutor_bookings'))


@app.route('/decline_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def decline_booking_r(booking_id):
    decline_booking(booking_id)
    booking = get_booking(booking_id)
    student_id = booking[1]
    insert_notification_for_student(student_id, "Booking Declined", "Your tutoring booking has been declined.", "booking", False)
    flash("Booking Declined", "info")
    return redirect(url_for('tutor_bookings'))

@app.route('/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def cancel_booking_r(booking_id):
    cancel_booking(booking_id)
    booking = get_booking(booking_id)
    student_id = booking[1]
    insert_notification_for_student(student_id, "Booking Cancelled", "Your tutoring booking has been cancelled.", "booking", False)
    flash("Booking cancelled successfully.", "warning")
    return redirect(url_for('tutor_bookings'))

@app.route('/complete_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def complete_booking_r(booking_id):
    complete_booking(booking_id)
    booking = get_booking(booking_id)
    student_id = booking[1]
    insert_notification_for_student(student_id, "Lesson Completed", "Your tutoring lesson has been marked as completed.", "booking", False)
    flash("Lesson marked as completed.", "success")
    return redirect(url_for('tutor_bookings'))



@app.route('/update_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def update_booking_r(booking_id):

    booking = get_booking(booking_id)

    if request.method == 'POST':

        tutor_id = request.form['tutor_id']
        booking_date = request.form['booking_date']
        booking_time = request.form['booking_time']

        update_booking(booking_id, tutor_id, booking_date, booking_time)

        flash("Booking updated successfully", "success")

        return redirect(url_for('bookings'))

    return render_template('update_booking.html', booking=booking)

@app.route("/bookings")
@login_required
def bookings():

    student_id = session["student_id"]

    bookings = get_student_bookings(student_id)

    return render_template(
        "bookings.html",
        bookings=bookings
    )







@app.route('/my_bookings')
@login_required
def my_bookings():
    user_id = session.get('user_id')

    student = get_student_by_user_id(user_id)

    if not student:
        return "No student profile found"

    student_id = student[0]
    bookings = get_student_bookings(student_id)
    today = date.today()
    return render_template('my_bookings.html', bookings=bookings, today=today)
@app.route('/tutor_bookings')
@login_required
def tutor_bookings():
    user_id = session['user_id']
    
    tutor = get_tutor_by_user_id(user_id)
    
    if not tutor:
        flash("No tutor profile found")
        return redirect(url_for('student_dashboard'))
    
    tutor_id = tutor[0]
    bookings = get_tutor_bookings(tutor_id)
    today = date.today()
    return render_template('tutor_bookings.html', bookings=bookings,today=today)




def insert_payments_r():

    if request.method == 'POST':

        booking_id = request.form['booking_id']
        student_id = request.form['student_id']
        amount = request.form['amount']
        payment_method = request.form['payment_method']

        insert_payment( booking_id,amount,payment_method)
        insert_notification(student_id,"Your payment has been received.")

        flash("Payment recorded successfully", "success")
        bookings = get_booking()

        return redirect(url_for('payments'))

        

    return render_template('payments.html', bookings=bookings)

@app.route('/tutor/mark_paid/<int:booking_id>', methods=['POST'])
@login_required
def tutor_mark_paid_route(booking_id):
    mark_booking_paid(booking_id)
    user_id = get_student_user_id_from_booking(booking_id)
    if user_id:
        add_payment_notification(user_id)
    flash("Booking marked as PAID and confirmed.", "success")
    return redirect(url_for('tutor_bookings'))

@app.route('/tutor/mark_unpaid/<int:booking_id>', methods=['POST'])
@login_required
def tutor_mark_unpaid_route(booking_id):
    mark_booking_unpaid(booking_id)
    flash("Booking marked as unpaid.", "warning")
    return redirect(url_for('tutor_bookings'))

@app.route('/update_payments/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def update_payments_route(payment_id):

    payment = get_payments(payment_id)

    if request.method == 'POST':

        amount = request.form['amount']
        payment_method = request.form['payment_method']
        payment_status = request.form['payment_status']
        transaction_code = request.form['transaction_code']

        update_payment(payment_id,amount,payment_method, payment_status,transaction_code)

        flash("Payment updated successfully", "success")
        

        return redirect(url_for('payments'))

        return render_template('edit_payment.html',payment=payment)
    
@app.route('/confirm_payments/<int:payment_id>')
@login_required
def confirm_payment_route(payment_id):



    flash("Payment confirmed", "success")
    notifications = insert_notification

    return redirect(url_for('payments'))

@app.route('/cancel_payments/<int:payment_id>')
@login_required
def cancel_payments_route(payment_id):



    flash("Payment cancelled", "warning")

    return redirect(url_for('payments'))

@app.route('/reviews')
@login_required
def reviews():

    reviews = get_review()

    return render_template('reviews.html',reviews=reviews)




   
@app.route('/insert_reviews', methods=['GET', 'POST'])
@login_required
def insert_reviews_r():

    selected_tutor_id = request.args.get('tutor_id')
    bookings = get_all_bookings()

    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        tutor_id = request.form.get('tutor_id')
        user_id = session.get('user_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        student_data = get_student_by_user_id(user_id)
        student_id = student_data[0]

        student = get_user_by_id(user_id)
        student_name = student[1]

        insert_review(booking_id, tutor_id, student_id, rating, comment)

        # with title
        insert_notification(tutor_id, "New Review", f"you have a new review from {student_name}.", "review", False)

        flash("Review submitted successfully", "success")
        return redirect(url_for('reviews'))

    return render_template('reviews.html', bookings=bookings, selected_tutor_id=selected_tutor_id)
@app.route('/availability')
@login_required
def availability():

    availability = get_tutor_availability()

    return render_template('availability.html',availability=availability)

@app.route('/add_availability', methods=['GET', 'POST'])
@login_required
def add_availability():

    if request.method == 'POST':

        tutor_id = request.form['tutor_id']
        available_date = request.form['available_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        insert_availability(tutor_id,available_date,start_time, end_time)

        flash("Availability added successfully", "success")

        return redirect(url_for('availability'))

    return render_template('add_availability.html')



@app.route('/update_availability/<int:availability_id>', methods=['GET', 'POST'])
@login_required
def update_availability_r(availability_id):

    availability = get_availability(availability_id)

    if request.method == 'POST':

        tutor_id = request.form['tutor_id']
        available_date = request.form['available_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        update_availability(availability_id,tutor_id,available_date,start_time,end_time)
        insert_notification(tutor_id,"Your availability has been updated.")
    
        flash("Availability updated successfully", "success")

        return redirect(url_for('availability'))

    return render_template('edit_availability.html',availability=availability)

@app.route('/notifications')
@login_required
def notifications():

    notifications = get_notification()

    return render_template('notifications.html',notifications=notifications)

@app.route('/insert_notification', methods=['GET', 'POST'])
@login_required
def add_notification():

    if request.method == 'POST':

        user_id = request.form['user_id']
        message = request.form['message']
        notification_type = request.form['notification_type']

        insert_notification(user_id,message, notification_type)
        

        flash("Notification added successfully", "success")

        return redirect(url_for('notifications'))

    return render_template('notifications.html')

@app.route('/update_notification/<int:notification_id>', methods=['GET', 'POST'])
@login_required
def edit_notification(notification_id):

    notification = get_notification(notification_id)

    if request.method == 'POST':

        message = request.form['message']
        notification_type = request.form['notification_type']

        update_notification(notification_id, message,notification_type)

        flash("Notification updated successfully", "success")

        return redirect(url_for('notifications'))

    return render_template('update_notification.html',notification=notification)

if __name__ == "__main__":
    app.run(debug=True)