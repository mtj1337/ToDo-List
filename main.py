import tkinter as tk
import customtkinter as ctk
import sqlite3
from tkinter import messagebox

# Function to create the database and table if they do not exist
def create_db():
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()

    # Create table if not exists (will not affect existing table structure)
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                      (id INTEGER PRIMARY KEY, task TEXT, completed INTEGER)''')

    # Add 'completed' column if it doesn't exist already
    try:
        cursor.execute('PRAGMA table_info(tasks)')
        columns = [column[1] for column in cursor.fetchall()]
        if 'completed' not in columns:
            cursor.execute('ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0')
    except sqlite3.DatabaseError as e:
        print("Error during schema modification:", e)

    conn.commit()
    conn.close()

# Function to add a task to the database
def add_task():
    task = entry_task.get()
    if task:
        conn = sqlite3.connect("todo_list.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, completed) VALUES (?, ?)", (task, 0))
        conn.commit()
        conn.close()
        load_tasks()
        entry_task.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Task cannot be empty!")

# Function to load tasks from the database into the list
def load_tasks():
    for widget in frame_tasks.winfo_children():
        widget.destroy()  # Clear all widgets (checkbuttons and buttons)

    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, completed FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    for task in tasks:
        task_id, task_text, completed = task
        var = tk.BooleanVar(value=bool(completed))

        # Create frame for each task to hold the checkbox and the delete button
        task_frame = ctk.CTkFrame(frame_tasks)
        task_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create a checkbox for each task
        checkbox = ctk.CTkCheckBox(task_frame, text=task_text, variable=var, 
                                   command=lambda var=var, task_id=task_id: toggle_task(var, task_id))
        checkbox.pack(side=tk.LEFT, anchor="w")

        # Create a small "X" label for deleting, always visible
        delete_x = ctk.CTkLabel(task_frame, text="✖", font=("Arial", 12), text_color="gray",
                                cursor="hand2", padx=5, pady=5)  # Added padding to increase clickable area
        delete_x.pack(side=tk.RIGHT, padx=5, pady=5)

        # Add a command to delete when the "X" is clicked
        delete_x.bind("<Button-1>", lambda event, task_id=task_id: delete_task(task_id))

        task_vars[task_id] = var  # Store the checkbox variable for future reference

# Function to toggle the completion status of a task
def toggle_task(var, task_id):
    new_status = 1 if var.get() else 0
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

# Function to delete a task by its ID
def delete_task(task_id):
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    load_tasks()  # Reload the tasks after deletion

# Function to toggle between Light and Dark themes (reversed)
def toggle_theme():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")  # Switch to Dark theme when currently in Light
    else:
        ctk.set_appearance_mode("Light")  # Switch to Light theme when currently in Dark

# Setup the main window
root = ctk.CTk()
root.title("To-Do List")
root.geometry("400x400")

# Create and load the database
create_db()

# Dictionary to store task variables
task_vars = {}

# Task entry field
entry_task = ctk.CTkEntry(root, width=300, placeholder_text="Enter a new task")
entry_task.pack(pady=10)

# Add task button
button_add_task = ctk.CTkButton(root, text="Add Task", command=add_task)
button_add_task.pack(pady=5)

# Frame for checkboxes and delete buttons
frame_tasks = ctk.CTkFrame(root)
frame_tasks.pack(pady=10, fill=tk.BOTH, expand=True)

# Theme toggle button
button_toggle_theme = ctk.CTkButton(root, text="Toggle Theme", command=toggle_theme)
button_toggle_theme.pack(pady=10)

# Load tasks on startup
load_tasks()

# Run the main loop
root.mainloop()
