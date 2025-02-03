import tkinter as tk
from tkinter import messagebox
import json
import time
import os
from datetime import datetime, timedelta

# File to store persistent data
DATA_FILE = "event_tracker.json"

# **New Timer System**
TOTAL_CYCLE_DURATION = 3 * 60 * 60 + 5 * 60  # 3 hours 5 minutes (11,100 seconds)
STATES = [
    ("Red", 5, 24 * 60),
    ("Red", 4, 24 * 60),
    ("Red", 3, 24 * 60),
    ("Red", 2, 24 * 60),
    ("Red", 1, 24 * 60),
    ("Green", 5, 12 * 60),
    ("Green", 4, 12 * 60),
    ("Green", 3, 12 * 60),
    ("Green", 2, 12 * 60),
    ("Green", 1, 12 * 60),
    ("Black", 5, 5 * 60),  # Cooldown (Only Black 5 allowed)
]

# Load saved state from file
def load_state():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return None

# Save state to file (Only called when "Set" or "Reset" is used)
def save_state(init_time):
    data = {"init_time": init_time}
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)
    print(f"Saved state: {data}")  # Debugging output

# Reset confirmation and action
def reset():
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset?"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        initialize_tracker()

# Initialize tracker only if no valid state is found
def initialize_tracker(force=False):
    global init_time

    if not force:
        saved_state = load_state()
        if saved_state and "init_time" in saved_state:
            init_time = saved_state["init_time"]
            return  # Do not reinitialize if valid data exists

    # If no valid state, set init_time to NOW
    init_time = time.time()
    save_state(init_time)
    update_display()

# Determine the current phase and state based on elapsed time
def update_state():
    global current_phase, current_state, init_time

    saved_state = load_state()
    if saved_state and "init_time" in saved_state:
        init_time = saved_state["init_time"]
    else:
        return  # No valid state, do nothing

    elapsed_time = (time.time() - init_time) % TOTAL_CYCLE_DURATION  # Keeps the time in a continuous loop

    cumulative_time = 0
    for phase, state, duration in STATES:
        cumulative_time += duration
        if elapsed_time < cumulative_time:
            current_phase = phase
            current_state = state
            return

# **Manually set phase and state**
def set_manual_state():
    global init_time

    selected_phase = phase_var.get()
    selected_state = int(state_var.get())

    # If user selects Black 4 - Black 1, set it to Black 5
    if selected_phase == "Black" and selected_state in {4, 3, 2, 1}:
        selected_state = 5

    # Find the correct offset in the cycle
    cumulative_time = 0
    for phase, state, duration in STATES:
        if phase == selected_phase and state == selected_state:
            break
        cumulative_time += duration

    # Set init_time so that we are exactly at the start of the selected phase/state
    init_time = time.time() - cumulative_time
    save_state(init_time)

    update_display()  # Update UI immediately

# **Adjust Display Time Based on Phase**
def get_adjusted_display_time(remaining_time):
    if current_phase == "Red":
        adjusted_time = remaining_time - (1 * 60 * 60 + 5 * 60)  # Offset by -1 hour 5 min
    elif current_phase == "Green":
        adjusted_time = remaining_time - (5 * 60)  # Offset by -5 minutes
    else:  # Black (No adjustment)
        adjusted_time = remaining_time

    return max(adjusted_time, 0)  # Ensure time never goes negative

# **Get User-Friendly Display Text**
def get_display_text():
    if current_phase == "Red":
        return f"Hanger Locked {current_state}"
    elif current_phase == "Green":
        return f"Hanger Unlocked {current_state}"
    else:
        return "Hanger Gassed"  # Black phase

# **Update Circle Colors**
def update_circles():
    colors = []

    if current_phase == "Red":
        colors = ["red"] * current_state + ["green"] * (5 - current_state)
    elif current_phase == "Green":
        colors = ["green"] * current_state + ["black"] * (5 - current_state)
    else:  # Black phase
        colors = ["black"] * 5

    for i, color in enumerate(colors):
        canvas.itemconfig(circle_ids[i], fill=color)

# **Update Display**
def update_display():
    update_state()  # Get current phase, state, and remaining time

    elapsed_time = (time.time() - init_time) % TOTAL_CYCLE_DURATION  # Keeps time within cycle
    remaining_time = TOTAL_CYCLE_DURATION - elapsed_time

    # Adjust Display Time
    adjusted_display_time = get_adjusted_display_time(remaining_time)

    remaining_phase = str(timedelta(seconds=int(adjusted_display_time)))

    phase_label.config(text=get_display_text(), fg="red" if current_phase == "Red" else "green" if current_phase == "Green" else "black")
    time_label.config(text=f"Time Remaining: {remaining_phase}")

    update_circles()  # Update circle colors

    root.after(1000, update_display)  # Refresh every second

# **Create UI**
root = tk.Tk()
root.title("Event Tracker")
root.geometry("400x300")

# Labels
phase_label = tk.Label(root, text="", font=("Arial", 16))
phase_label.pack(pady=10)

# **Canvas for Colored Circles**
canvas = tk.Canvas(root, width=250, height=50, bg="white", highlightthickness=0)
canvas.pack()

# Create 5 circles for phase visualization
circle_radius = 10
circle_spacing = 50
circle_ids = []
for i in range(5):
    x = 25 + i * circle_spacing
    y = 25
    circle = canvas.create_oval(x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius, fill="black", outline="gray")
    circle_ids.append(circle)

# Time Remaining Label
time_label = tk.Label(root, text="", font=("Arial", 14))
time_label.pack(pady=5)

# Frame to hold manual phase selection options in one row
manual_frame = tk.Frame(root)
manual_frame.pack(pady=10)

# **Dropdown for selecting phase**
phase_var = tk.StringVar(root)
phase_var.set("Red")
phase_dropdown = tk.OptionMenu(manual_frame, phase_var, "Red", "Green", "Black")
phase_dropdown.grid(row=0, column=0, padx=5)

# **Dropdown for selecting state**
state_var = tk.StringVar(root)
state_var.set("5")
state_dropdown = tk.OptionMenu(manual_frame, state_var, "5", "4", "3", "2", "1")
state_dropdown.grid(row=0, column=1, padx=5)

# **Button to manually set the phase and state**
manual_set_button = tk.Button(manual_frame, text="Set", command=set_manual_state, bg="blue", fg="white")
manual_set_button.grid(row=0, column=2, padx=5)

# **Reset button**
reset_button = tk.Button(root, text="Reset", command=reset, bg="gray", fg="white")
reset_button.pack(pady=20)

initialize_tracker()
update_display()
root.mainloop()
