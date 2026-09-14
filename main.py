from flask import Flask, render_template,request,redirect,url_for,flash,session
from flask_login import LoginManager, login_required, current_user
from database import *
from datetime import date, datetime


from flask_bcrypt import Bcrypt
from functools import wraps 

app = Flask(__name__)
app.secret_key = 'Gfghjk'


bcrypt = Bcrypt(app)

@app.route('/')
def home():
    
    return  render_template('index.html')

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

            print(f"DEBUG: Trying {email} as {role}")

            existing_user = check_user_exists(email)

            if existing_user:
                flash("User already exists, please login instead", "danger")
                return render_template('register.html')

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = (first_name, last_name, email, phone_number, role, hashed_password)

            insert_user(new_user)
            print("DEBUG: User inserted")

            user = check_user_exists(email)
            if not user:
                flash("Failed to retrieve new user", "danger")
                return render_template('register.html')

            user_id = user[0]
            print(f"DEBUG: user_id = {user_id}")

            if role == "student":
                insert_student(user_id, "", "", "Available")
                print("DEBUG: Student inserted")

            elif role == "tutor":
                
                insert_tutor(user_id, "General", "", 0, 0, "", "Available")
                print("DEBUG: Tutor inserted")

            flash("User created successfully, please login!", "success")
            return redirect(url_for('login'))

        

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
            session['name'] = f"{registered_user[1]} {registered_user[2]}"
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
                if not student:
                    cur.execute(
                        "INSERT INTO students (user_id) VALUES (%s)",
                        (registered_user[0],)
                    )
                    conn.commit()
                    student = get_student_by_user_id(registered_user[0])

                if not student:
                    flash("Student profile could not be created.", "danger")
                    return redirect(url_for("login"))

                session['student_id'] = student[0]
                return redirect(url_for("home"))

        else:
            flash("Incorrect password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/logout')
def logout():
    try:
        session.clear()
        flash("Logged out", "info")
    except:
        pass
    return redirect(url_for('login'))


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

@app.route('/edit_profile', methods=['GET', 'POST'])
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
        phone = request.form['phone']
        bio = request.form['bio']
        availability = request.form['availability']

        update_tutor(tutor_id, subject, qualification, experience_years, hourly_rate,phone, bio, availability)
        flash("Profile updated successfully", "success")
        return redirect(url_for('tutor_dashboard'))

    return render_template('edit_profile.html', tutor=tutor)


@app.route('/view_tutor/<int:tutor_id>')
@login_required
def view_tutor(tutor_id):
    tutor = get_tutor(tutor_id)
    if not tutor:
        flash("Tutor not found", "danger")
        return redirect(url_for('student_dashboard'))

   
    tutor_user_id = tutor[1]
    user_row = get_user_by_id(tutor_user_id) 
    reviews = get_reviews_for_tutor(tutor_id)
    
    print("DEBUG user_row:", user_row) 
    return render_template('view_tutors_profile.html',
                           tutor=tutor,
                           user=user_row,
                           reviews=reviews)

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
    if not tutor:
        flash("Tutor not found")
        return redirect(url_for('dashboard'))

    user_id = session.get('user_id')
    if not user_id:
        flash("Session expired, please login again")
        return redirect(url_for('login'))

   
    student = get_student_by_user_id(user_id)
    if not student:
        try:
            cur.execute(
                "INSERT INTO students (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            conn.commit()
            student = get_student_by_user_id(user_id)
        except Exception as e:
            conn.rollback()
            print(f"Failed to create student: {e}")
            flash("Could not create student profile")
            return redirect(url_for('login'))

    if not student:
        flash("Student profile not found")
        return redirect(url_for('login'))

    student_id = student[0]

    if request.method == 'POST':
        subject = request.form.get('subject')
        date_val = request.form.get('date')
        start = request.form.get('start_time')
        end = request.form.get('end_time')

        if not all([subject, date_val, start, end]):
            flash("Please fill all fields")
            return render_template('book_tutor.html', tutor=tutor, tutor_id=tutor_id)

        insert_booking(student_id, tutor_id, date_val, start, end, 'online', subject)

        tutor_user_id = get_tutor_user_id(tutor_id)
        if tutor_user_id:
            insert_notification_for_tutor(
                tutor_user_id,
                "New Booking",
                f"{session.get('name')} booked {subject} on {date_val}",
                "booking"
            )

        flash("Booking successful!")
        return redirect(url_for('my_bookings'))

    return render_template('book_tutor.html', tutor=tutor, tutor_id=tutor_id)
@app.route('/confirm_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def confirm_booking_r(booking_id):
    if request.method == 'POST':
        meet_link = request.form.get('meet_link') 
        confirm_booking(booking_id)
        update_booking_meet_link(booking_id, meet_link)

        booking = get_booking(booking_id)
        student_id = booking[1]
        tutor_id = booking[2] 
        student_row = get_student_by_student_id(student_id) 
        student_user_id = student_row[1]

        tutor = get_tutor(tutor_id) 
        tutor_user = get_user_by_id(tutor[1])
        tutor_name = tutor_user[1]

        insert_notification_for_student(
            student_user_id,
            "Booking Confirmed",
            f"Your booking with {tutor_name} is confirmed. Link: {meet_link}",
            "booking",
            tutor_id,
            False
        )
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




@app.route('/my_bookings')
@login_required
def my_bookings():
    user_id = session.get('user_id')
    if not user_id:
        try:
            user_id = current_user.id
        except:
            pass

    student = get_student_by_user_id(user_id)
    if not student:
        return f"No student profile found for user_id {user_id}"

    student_id = student[0]

    from database import cur
    cur.execute("""
        SELECT b.booking_id, b.tutor_id, b.booking_date, b.start_time, b.end_time,
               b.booking_status, b.meet_link,
               u.first_name, u.last_name
        FROM bookings b
        JOIN tutors t ON b.tutor_id = t.tutor_id
        JOIN users u ON t.user_id = u.user_id
        WHERE b.student_id = %s
        ORDER BY b.booking_id DESC
    """, (student_id,))
    bookings = cur.fetchall()

    return render_template('my_bookings.html', bookings=bookings)
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



@app.route('/tutor/mark-paid/<int:booking_id>', methods=['POST'])
def tutor_mark_paid(booking_id):
    amount = request.form.get('amount')
    code = request.form.get('transaction_code') 

    cur.execute("INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_code, payment_date) VALUES (%s,%s,'M-Pesa','Paid',%s,NOW())", (booking_id, amount, code))
    cur.execute("UPDATE bookings SET payment_status='paid' WHERE booking_id=%s", (booking_id,))
    conn.commit()

    cur.execute("SELECT student_id FROM bookings WHERE booking_id=%s", (booking_id,))
    row = cur.fetchone()
    if row:
        student_id = row[0]
        cur.execute("SELECT user_id FROM students WHERE student_id=%s", (student_id,))
        s_row = cur.fetchone()
        if s_row:
            student_user_id = s_row[0]
            
            cur.execute("""
                INSERT INTO notifications (user_id, title, message, notification_type, is_read, sent_at)
                VALUES (%s, %s, %s, 'payment', FALSE, NOW())
            """, (student_user_id, "Payment Confirmed", f"Your payment of Ksh {amount} (Code: {code}) has been confirmed! Booking #{booking_id} is now PAID."))
            conn.commit()
    flash("Payment saved ")
    return redirect(url_for('tutor_bookings'))

@app.route('/payments')
@login_required
def payments():
    user_id = session['user_id']
    student = get_student_by_user_id(user_id)
    student_id = student[0]
    cur.execute("SELECT p.payment_id, p.booking_id, p.amount, p.payment_method, p.payment_status, p.transaction_code, p.payment_date FROM payments p JOIN bookings b ON p.booking_id = b.booking_id WHERE b.student_id = %s", (student_id,))
    payments = cur.fetchall()
    return render_template("payments.html", payments=payments)

@app.route('/tutor/mark_unpaid/<int:booking_id>', methods=['POST'])
@login_required
def tutor_mark_unpaid(booking_id):
    mark_booking_unpaid(booking_id)
    flash("Booking marked as unpaid.", "warning")
    return redirect(url_for('tutor_bookings'))

@app.route('/student/payments')
def student_payments():
    student_id = get_student_id_by_user(session['user_id'])
    payments = get_student_payments(student_id)
    return render_template('student_payments.html', payments=payments)


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




   


@app.route('/insert_reviews', methods=['GET','POST'])
@app.route('/insert_reviews/<int:tutor_id>', methods=['GET', 'POST'])
@login_required
def insert_reviews_page(tutor_id=None):
    user_id = session.get('user_id')

    if get_tutor_by_user_id(user_id):
        flash("Tutors cannot leave reviews.", "danger")
        return redirect(url_for('tutor_dashboard'))

    student_data = get_student_by_user_id(user_id)
    if not student_data:
        flash("Only students can leave reviews.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        tutor_name = request.form.get('tutor_name')
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        if not booking_id or not tutor_name:
            flash("Booking ID and Tutor Name required", "danger")
            return redirect(url_for('insert_reviews_page'))

        
        cur.execute("""
            SELECT t.tutor_id FROM tutors t
            JOIN users u ON t.user_id = u.user_id
            WHERE u.first_name ILIKE %s OR u.last_name ILIKE %s OR CONCAT(u.first_name,' ',u.last_name) ILIKE %s
        """, (f"%{tutor_name}%", f"%{tutor_name}%", f"%{tutor_name}%"))
        found = cur.fetchone()
        if not found:
            flash(f"Tutor '{tutor_name}' not found", "danger")
            return redirect(url_for('insert_reviews_page'))

        form_tutor_id = found[0]

       

        student_id = student_data[0]
        student_user = get_user_by_id(user_id)
        student_name = student_user[1] if student_user else "A student"

        tutor_row = get_tutor(form_tutor_id)
        if not tutor_row:
            flash("Tutor not found", "danger")
            return redirect(url_for('reviews'))

        tutor_user_id = tutor_row[1]

        insert_reviews(booking_id, form_tutor_id, student_id, rating, comment)
        insert_notification_for_tutor(tutor_user_id, "New Review", f"You have a new review from {student_name}.", "review")

        flash("Review submitted successfully", "success")
        return redirect(url_for('reviews'))
    selected_tutor_id = tutor_id 
    bookings = get_all_bookings()
    cur.execute("SELECT tutor_id, user_id FROM tutors")
    tutors = cur.fetchall()
    return render_template('reviews.html', bookings=bookings, tutors=tutors, selected_tutor_id=selected_tutor_id)

@app.route('/tutor/<int:tutor_id>/reviews')
@login_required
def tutor_reviews(tutor_id):
    tutor = get_tutor(tutor_id)
    reviews = get_reviews_for_tutor(tutor_id)
    

    return render_template('tutor_reviews.html',  tutor=tutor, reviews=reviews,)

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
    user_id = session.get('user_id')
    
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE", (user_id,))
    conn.commit()
    cur.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY sent_at DESC", (user_id,))
    notifications = cur.fetchall()
    cur.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY sent_at DESC", (user_id,))
    notifications = cur.fetchall()

    return render_template('notifications.html', notifications=notifications)

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


@app.route('/mark_read/<int:notification_id>')
@login_required
def mark_read(notification_id):
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE notification_id = %s", (notification_id,))
    conn.commit()
    return redirect(url_for('notifications'))
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)