from tkinter import *
from tkinter import messagebox
import sqlite3 as sql

# --- Database Setup ---
conn = sql.connect('scheduler.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        instructor TEXT NOT NULL,
        day TEXT NOT NULL,
        time_slot TEXT NOT NULL
    )
''')
conn.commit()

# --- Function Definitions ---
def add_course():
    name = course_name.get()
    instructor = course_instructor.get()
    day = course_day.get()
    time_slot = course_time.get()

    if not name or not instructor or not day or not time_slot:
        messagebox.showerror("Error", "Please fill all fields.")
        return

    # Check for schedule conflicts
    cursor.execute('SELECT * FROM courses WHERE day = ? AND time_slot = ?', (day, time_slot))
    if cursor.fetchone():
        messagebox.showwarning("Conflict", "Time slot already taken!")
        return

    cursor.execute('INSERT INTO courses (name, instructor, day, time_slot) VALUES (?, ?, ?, ?)', (name, instructor, day, time_slot))
    conn.commit()
    messagebox.showinfo("Success", "Course added successfully.")
    clear_inputs()
    display_courses()

def display_courses():
    course_listbox.delete(0, END)

    # Mapping days to numeric order
    day_order = {
        "Monday": 1, "Tuesday": 2, "Wednesday": 3,
        "Thursday": 4, "Friday": 5, "Saturday": 6
    }

    cursor.execute('SELECT name, instructor, day, time_slot FROM courses')
    all_courses = cursor.fetchall()

    def sort_key(course):
        day = course[2]
        time_range = course[3]
        try:
            start_time = int(time_range.strip().split(":")[0])  # "9:00-10:00" -> 9
        except:
            start_time = 0
        return (day_order.get(day, 99), start_time)

    sorted_courses = sorted(all_courses, key=sort_key)

    for row in sorted_courses:
        course_listbox.insert(END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

def delete_selected():
    try:
        selected = course_listbox.get(ACTIVE)
        name = selected.split('|')[0].strip()
        cursor.execute('DELETE FROM courses WHERE name = ?', (name,))
        conn.commit()
        messagebox.showinfo("Deleted", "Course removed.")
        display_courses()
    except:
        messagebox.showerror("Error", "No course selected.")

def clear_inputs():
    course_name.delete(0, END)
    course_instructor.delete(0, END)
    course_day.set("")
    course_time.set("")

def exit_app():
    conn.close()
    root.destroy()

# --- GUI Setup ---
root = Tk()
root.title("College Course Scheduler")
root.geometry("700x520")
root.config(bg="#dff5f3")

Label(root, text="College Course Scheduler", font=("Helvetica", 18, "bold"), bg="#dff5f3").pack(pady=10)

form_frame = Frame(root, bg="#dff5f3")
form_frame.pack(pady=5)

Label(form_frame, text="Course Name:", font=("Arial", 12), bg="#dff5f3").grid(row=0, column=0, padx=10, pady=5, sticky=E)
course_name = Entry(form_frame, font=("Arial", 12), width=30)
course_name.grid(row=0, column=1, pady=5)

Label(form_frame, text="Instructor:", font=("Arial", 12), bg="#dff5f3").grid(row=1, column=0, padx=10, pady=5, sticky=E)
course_instructor = Entry(form_frame, font=("Arial", 12), width=30)
course_instructor.grid(row=1, column=1, pady=5)

Label(form_frame, text="Day:", font=("Arial", 12), bg="#dff5f3").grid(row=2, column=0, padx=10, pady=5, sticky=E)
course_day = StringVar()
OptionMenu(form_frame, course_day, "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday").grid(row=2, column=1, sticky=W)

Label(form_frame, text="Time Slot:", font=("Arial", 12), bg="#dff5f3").grid(row=3, column=0, padx=10, pady=5, sticky=E)
course_time = StringVar()
OptionMenu(
    form_frame, course_time,
    "9:00-10:00", "10:00-11:00", "11:00-12:00",
    "12:00-1:00", "2:00-3:00", "3:00-4:00", "4:00-5:00"
).grid(row=3, column=1, sticky=W)

Button(root, text="Add Course", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=add_course).pack(pady=10)

course_listbox = Listbox(root, font=("Courier", 12), width=80, height=10, bg="white")
course_listbox.pack(pady=10)

Button(root, text="Delete Selected", font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", command=delete_selected).pack(pady=5)
Button(root, text="Exit", font=("Arial", 12), bg="gray", fg="white", command=exit_app).pack(pady=5)

display_courses()
root.mainloop()
