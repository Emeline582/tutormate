import psycopg2


conn = psycopg2.connect(host='localhost',port=5432,user='postgres',password='Emmy3986',dbname='tutormate')
cur = conn.cursor()

conn.autocommit = True   





def count_upcoming_bookings(student_id):
    cur.execute("SELECT COUNT(*)FROM bookings WHERE student_id = %s AND booking_status='Confirmed'", (student_id,))

    return cur.fetchone()[0]


def count_completed_bookings(student_id):
    cur.execute(" SELECT COUNT(*) FROM bookings WHERE student_id=%s AND booking_status='Completed'",(student_id,))

    return cur.fetchone()[0]



def count_student_pending_payments(student_id):
        cur.execute("SELECT COUNT(*) FROM payments p JOIN bookings b ON p.booking_id = b.booking_id WHERE b.student_id = %s AND p.payment_status = 'Pending'", (student_id,))
        return cur.fetchone()[0]

def count_tutor_bookings(tutor_id):

    cur.execute(" SELECT COUNT(*) FROM bookings WHERE tutor_id = %s", (tutor_id,))

    return cur.fetchone()[0]

def count_tutor_upcoming_bookings(tutor_id):

    cur.execute(" SELECT COUNT(*) FROM bookings WHERE tutor_id = %s AND booking_status = 'Confirmed'", (tutor_id,))

    total = cur.fetchone()[0]

    return total



def get_user(email):
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    return cur.fetchone()

def get_user_by_id(user_id):
    cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    return cur.fetchone()

def delete_user(user_id):
    cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    cur.commit()
   
def update_user(first_name, last_name, email, phone,user_id):
    cur.execute(" UPDATE users SET first_name=%s,  last_name=%s,  email=%s,  phone=% WHERE user_id=%s", (first_name, last_name, email, phone, user_id))
    conn.commit()





def get_tutor(tutor_id):
    cur.execute("select * from tutors where tutor_id = %s",(tutor_id,))
    tutor_data = cur.fetchone()
    return tutor_data

def get_tutors():
   
    cur.execute("""
        SELECT t.tutor_id, t.user_id, t.subject, t.qualification,
               t.experience_years, t.hourly_rate, t.bio, t.availability,
               u.first_name, u.last_name
        FROM tutors t
        JOIN users u ON t.user_id = u.user_id
    """)
    data = cur.fetchall()
    
    return data

def get_tutor_by_user_id(user_id):
    cur.execute(
        "SELECT * FROM tutors WHERE user_id = %s",(user_id,))
    return cur.fetchone()



def update_tutor(tutor_id, subject, qualification, experience_years, hourly_rate, bio, availability):
    cur.execute("""
        UPDATE tutors SET subject=%s, qualification=%s, experience_years=%s,
        hourly_rate=%s, bio=%s, availability=%s WHERE tutor_id=%s
    """, (subject, qualification, experience_years, hourly_rate, bio, availability, tutor_id))
    conn.commit()

def delete_tutor( tutor_id):
    cur.execute("DELETE FROM tutors WHERE tutor_id=%s", (tutor_id,))

    conn.commit()

def get_tutor_availability(tutor_id):
    cur.execute("SELECT *FROM availability WHERE tutor_id=%s ORDER BY available_date, start_time", (tutor_id,))
    availability = cur.fetchall()
    return availability




def get_student():
    cur.execute("select * from students")
    students_data = cur.fetchall()
    return students_data

def check_user_exists(email):
  
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        result = cur.fetchone()
        return result
    

def insert_user(user):
  
        cur.execute("""
            INSERT INTO users
            (first_name,last_name,email,phone_number,role,password)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, user)
        conn.commit()
      

def insert_student(user_id, education="", subjects="", availability="Available"):
    
        cur.execute(
            "INSERT INTO students (user_id) VALUES (%s)",
            (user_id,)
        )
        conn.commit()
       

def insert_tutor(user_id, subject="General", bio="", experience=0, price=0, education="", availability="Available"):
   
        cur.execute(
            "INSERT INTO tutors (user_id) VALUES (%s)",
            (user_id,)
        )
        conn.commit()
        
    

def get_student_by_user_id(user_id):
    cur.execute(
        "SELECT * FROM students WHERE user_id=%s",(user_id,))
    return cur.fetchone()

def update_student( student_id, school_name, education_level):
    cur.execute("UPDATE students SET school_name=%s,education_level=%s WHERE student_id=%s", (school_name, education_level, student_id))

    conn.commit()

def delete_student( student_id):
    cur.execute("DELETE FROM students WHERE student_id=%s", (student_id,))

    conn.commit()


def insert_booking(student_id, tutor_id, booking_date, start_time, end_time, session_mode, notes):
    cur.execute("""
        INSERT INTO bookings(student_id, tutor_id, booking_date, start_time, end_time, session_mode, notes)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """, (student_id, tutor_id, booking_date, start_time, end_time, session_mode, notes))
    conn.commit()
def get_booking(booking_id):
    cur.execute("SELECT * FROM bookings WHERE booking_id=%s", (booking_id,))
    bookings = cur.fetchone()
    return bookings

def get_booking(booking_id):
    cur.execute("SELECT * FROM bookings WHERE booking_id=%s", (booking_id,))
    bookings = cur.fetchone()
    return bookings

def get_my_bookings(student_id):
    cur.execute("""
        SELECT b.booking_id, b.tutor_id, b.booking_date, b.start_time, b.end_time,
               b.m_ode, b.status, u.first_name, u.last_name
        FROM bookings b
        JOIN tutors t ON b.tutor_id = t.tutor_id
        JOIN users u ON t.user_id = u.user_id
        WHERE b.student_id = %s
        ORDER BY b.booking_id DESC
    """, (student_id,))
    rows = cur.fetchall()
    return rows
def get_all_bookings():
    cur.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
    bookings = cur.fetchall()
    return bookings
def update_booking(booking_id, tutor_id, booking_date, booking_time):
    cur.execute("UPDATE bookings SET tutor_id=%s, booking_date=%s, start_time=%s WHERE booking_id=%s", (tutor_id, booking_date, booking_time, booking_id))
    conn.commit()
        
def cancel_booking(booking_id):
    cur.execute("UPDATE bookings SET booking_status='Cancelled' WHERE booking_id=%s ", (booking_id,))
    conn.commit()

def confirm_booking(booking_id):
    cur.execute("UPDATE bookings SET booking_status='Confirmed', notes='Confirmed' WHERE booking_id=%s ", (booking_id,))
    conn.commit()

def update_booking_meet_link(booking_id, meet_link):
    cur.execute("UPDATE bookings SET meet_link=%s, booking_status='Confirmed' WHERE booking_id=%s", (meet_link, booking_id))
    conn.commit()

def decline_booking(booking_id):
    cur.execute("UPDATE bookings SET booking_status='Declined', notes='Declined' WHERE booking_id=%s", (booking_id,))
    conn.commit()

def complete_booking(booking_id):
    cur.execute("UPDATE bookings SET booking_status='Completed', notes='Completed' WHERE booking_id=%s ", (booking_id,))
    conn.commit()







def insert_payment(booking_id, amount, payment_method, payment_status, transaction_code):
    cur.execute("INSERT INTO payments(booking_id,amount,payment_method,payment_status,transaction_code) VALUES(%s,%s,%s,%s,%s)", 
                (booking_id,amount,payment_method,payment_status=="pending",transaction_code))
    conn.commit()

def get_payments(payment_id):
    cur.execute("select * from payments WHERE payment_id=%s", (payment_id,))
    payments_data = cur.fetchone()
    return payments_data
def get_all_payments():
    cur.execute("SELECT * FROM payments")
    return cur.fetchall()
def mark_booking_paid(booking_id):
    cur.execute("UPDATE bookings SET payment_status='paid', booking_status='confirmed' WHERE booking_id=%s", (booking_id,))
    conn.commit()

def mark_booking_unpaid(booking_id):
    cur.execute("UPDATE bookings SET payment_status='unpaid', booking_status='pending' WHERE booking_id=%s", (booking_id,))
    conn.commit()
def insert_payment(booking_id, amount, code):
    cur.execute("INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_code, payment_date) VALUES (%s, %s, 'M-Pesa', 'Paid', %s, NOW())", (booking_id, amount, code))
    conn.commit()

def get_student_payments(student_id):
    cur.execute("SELECT p.payment_id, p.booking_id, p.amount, p.payment_method, p.payment_status, p.transaction_code, p.payment_date FROM payments p JOIN bookings b ON p.booking_id = b.booking_id WHERE b.student_id = %s", (student_id,))
    return cur.fetchall()
def get_student_user_id_from_booking(booking_id):
    cur.execute("SELECT s.user_id FROM bookings b JOIN students s ON b.student_id = s.student_id WHERE b.booking_id=%s", (booking_id,))
    row = cur.fetchone()
    return row[0] if row else None

def add_payment_notification(user_id):
    cur.execute("INSERT INTO notifications (user_id, title, message, notification_type) VALUES (%s, %s, %s, %s)", (user_id, "Payment Received", "Tutor confirmed payment. Lesson confirmed!", "payment"))
    conn.commit()
def confirm_payments(payment_id):
    cur.execute(" UPDATE paymentsSET payment_status='Paid'WHERE payment_id=%s", (payment_id,))
    payments_data = cur.fetchone()
    return payments_data

def get_pending_payments(payment_id):
    cur.execute(" UPDATE paymentsSET payment_status='Pending'WHERE payment_id=%s", (payment_id,))
    payments_data = cur.fetchone()
    return payments_data


def update_payment(payment_id, booking_id, amount, payment_method, payment_status,transaction_code):

    cur.execute("UPDATE payments SET booking_id = %s,amount = %s,payment_method = %s,payment_status = %s, transaction_code =%s WHERE payment_id = %s",
                 (booking_id,amount,payment_method,payment_status,payment_id,transaction_code))

    conn.commit()


def get_tutor_id_by_user(user_id):
    cur.execute("SELECT tutor_id FROM tutors WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None

def get_student_id_by_user(user_id):
    cur.execute("SELECT student_id FROM students WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None

def get_payment_by_booking(booking_id):
    cur.execute("SELECT payment_id FROM public.payments WHERE booking_id = %s", (booking_id,))
    return cur.fetchone()

def get_booking_amount(booking_id):
    cur.execute("SELECT amount FROM public.payments WHERE booking_id = %s", (booking_id,))
    row = cur.fetchone()
    return row[0] if row else 0

def update_payment_to_paid(booking_id, mpesa_code):
    cur.execute("""
        UPDATE public.payments
        SET payment_method = 'mpesa',
            payment_status = 'paid',
            transaction_code = %s,
            payment_date = CURRENT_TIMESTAMP
        WHERE booking_id = %s
    """, (mpesa_code, booking_id))
    conn.commit()

def insert_payment_as_paid(booking_id, amount, mpesa_code):
    cur.execute("""
        INSERT INTO public.payments (booking_id, amount, payment_method, payment_status, transaction_code)
        VALUES (%s, %s, 'mpesa', 'paid', %s)
    """, (booking_id, amount, mpesa_code))
    conn.commit()

def get_student_payments(student_id):
    cur.execute("""
        SELECT p.payment_id, p.amount, p.payment_method,
               p.payment_status, p.transaction_code, p.payment_date, b.booking_id
        FROM public.payments p
        JOIN public.bookings b ON p.booking_id = b.booking_id
        WHERE b.student_id = %s
        ORDER BY p.payment_date DESC
    """, (student_id,))
    return cur.fetchall()

def get_student_payments(student_id):
    cur.execute("""
        SELECT p.payment_id, p.booking_id, p.amount,
               p.payment_method, p.payment_status,
               p.transaction_code, p.payment_date,
               u.first_name as tutor_name
        FROM payments p
        JOIN bookings b ON p.booking_id = b.booking_id
        JOIN tutors t ON b.tutor_id = t.tutor_id
        JOIN users u ON t.user_id = u.user_id
        WHERE b.student_id = %s
        ORDER BY p.payment_date DESC
    """, (student_id,))
    return cur.fetchall()
def get_tutor_bookings(tutor_id):
    cur.execute("""
        SELECT
            b.booking_id,
            b.student_id,
            b.tutor_id,
            b.booking_date,
            b.start_time,
            b.end_time,
            'online' as session_mode,  
            b.booking_status,
            COALESCE(b.payment_status, 'unpaid') as payment_status,
            u.first_name,
            u.last_name
        FROM bookings b
        JOIN students s ON b.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE b.tutor_id = %s
        ORDER BY b.booking_id DESC
    """, (tutor_id,))
    return cur.fetchall()
    

def insert_reviews(booking_id, tutor_id, student_id, rating, comment):
    cur.execute("""
        INSERT INTO reviews (booking_id, tutor_id, student_id, rating, comment, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING review_id;
    """, (booking_id, tutor_id, student_id, rating, comment))
    return cur.fetchone()[0]

def get_review():
    cur.execute("select * from reviews")
    review_data = cur.fetchall()
    return review_data

def get_reviews_for_tutor(tutor_id):
    cur.execute("""
        SELECT r.rating, r.comment, r.created_at,
               u.first_name, u.last_name
        FROM reviews r
        JOIN students s ON r.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE r.tutor_id = %s
        ORDER BY r.created_at DESC
    """, (tutor_id,))
    return cur.fetchall()


def update_review( review_id, rating, comment):
    cur.execute("UPDATE reviews SET rating=%s,comment=%s WHERE review_id=%s", (rating, comment, review_id))

    conn.commit()

def delete_review( review_id):
    cur.execute("DELETE FROM reviews WHERE review_id=%s", (review_id,))

    conn.commit()

def get_tutor_reviews( tutor_id):
    cur.execute("SELECT * FROM reviews WHERE tutor_id=%s ORDER BY review_id ", (tutor_id,))
    reviews = cur.fetchall()
    return reviews

def insert_availability(tutor_id, available_day, start_time, end_time, availability_status):
    cur.execute("INSERT INTO tutor_availability(tutor_id,available_day,start_time,end_time,availability_status) VALUES(%s,%s,%s,%s,%s)", (tutor_id,available_day,start_time,end_time,availability_status))
    conn.commit()



def get_availability(availability_id):
    cur.execute("select * from availability WHERE availability_id=%s",(availability_id,))
    availability_data = cur.fetchone()
    return availability_data

def update_availability(available_date, start_time, end_time,availability_id):
    cur.execute(" UPDATE availability SET available_date=%s,start_time=%s,end_time=%s WHERE availability_id=%s",(available_date, start_time, end_time, availability_id))
    conn.commit()


def delete_availability( availability_id):
    cur.execute("DELETE FROM availability WHERE availability_id=%s", (availability_id,))
    conn.commit()

def get_available_slots():
    cur.execute(" SELECT * FROM availability WHERE status='Available' ORDER BY available_date, start_time")
    slots = cur.fetchall()
    return slots

def get_available_tutors( available_date):
    cur.execute("SELECT * FROM availability WHERE available_date=%s AND status='Available'", (available_date,))
    tutors = cur.fetchall()
    return tutors
                
def mark_slot_booked( availability_id):
    cur.execute("UPDATE availability SET status='Booked'  WHERE availability_id=%s", (availability_id,))
    conn.commit()

def mark_slot_available(availability_id):
    cur.execute("UPDATE availability SET status='Available' WHERE availability_id=%s", (availability_id,))
    conn.commit()


def insert_notification(user_id, title, message, notification_type="review", is_read=False):
    cur.execute("""
        INSERT INTO notifications (user_id, title, message, notification_type, is_read)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, title, message, notification_type, is_read))
    conn.commit()
    

def insert_notification_for_tutor(tutor_user_id, title, message, notification_type, is_read=False):
    cur.execute("""
        INSERT INTO notifications (user_id, title, message, notification_type, is_read, sent_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (tutor_user_id, title, message, notification_type, is_read))
    conn.commit()



def insert_notification_for_student(student_user_id, title, message, type, tutor_id, is_read=False):
    cur.execute("""
        INSERT INTO notifications(user_id, title, message, notification_type, is_read, tutor_id)
        VALUES(%s,%s,%s,%s,%s,%s)
    """, (student_user_id, title, message, type, is_read, tutor_id))
    conn.commit()
def get_student_name(student_id):
    student = get_student(student_id) 
    return student[1]

def get_tutor_user_id(tutor_id):
    tutor = get_tutor(tutor_id)
    return tutor[1] 

def get_student_by_student_id(student_id):
    cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    return cur.fetchone()

def get_user_by_id(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cur.fetchone()
def get_notification():
    cur.execute("select * from notifications")
    notification_data = cur.fetchall()
    return notification_data

def get_notifications_for_user(user_id):
    cur.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY sent_at DESC", (user_id,))
    return cur.fetchall()
def mark_as_read(notification_id):
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE notification_id = %s", (notification_id,))
    conn.commit()
def update_notification( notification_id,title,message):
    cur.execute("UPDATE notifications SET title=%s,message=%sWHERE notification_id=%s", (title, message, notification_id))
    conn.commit()


def delete_notification( user_id):
    cur.execute("DELETE FROM notifications WHERE user_id=%s", (user_id,))
    conn.commit()


def get_user_notifications( user_id):
    cur.execute(" SELECT * FROM notifications WHERE user_id=%s ORDER BY notification_id DESC", (user_id,))
    notifications = cur.fetchall()
    return notifications

def send_booking_notification( user_id, booking_id):
    cur.execute(" INSERT INTO notifications (user_id, title, message, status) VALUES (    %s,   'Booking Confirmation',   %s,   'Unread'  )", ( user_id, f'Your booking #{booking_id} has been successfully created.' ))
    conn.commit()

def mark_as_read( notification_id):
    cur.execute("UPDATE notifications SET status='Read' WHERE notification_id=%s", (notification_id,))
    conn.commit()

def mark_as_unread( notification_id):
    cur.execute("UPDATE notifications SET status='Unread' WHERE notification_id=%s", (notification_id,))
    conn.commit()

def count_notifications():
    cur.execute(" SELECT COUNT(*) FROM notifications ")
    total = cur.fetchone()[0]
    return total

def get_student_bookings(student_id):
    cur.execute("""
        SELECT
            b.booking_id,
            b.tutor_id,
            b.booking_date,
            b.start_time,
            b.end_time,
            b.m_ode,
            b.booking_status            
        FROM bookings b
        JOIN tutors t ON b.tutor_id = t.tutor_id
        JOIN users u ON t.user_id = u.user_id
        WHERE b.student_id = %s
        ORDER BY b.booking_id DESC        
    """, (student_id,))
    bookings = cur.fetchall()
    return bookings
