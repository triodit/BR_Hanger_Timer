import tkinter as tk
from tkinter import messagebox
import json
import time
import os
from datetime import datetime, timedelta

# File to store persistent data
DATA_FILE = "event_tracker.json"

# Define phases, states, and durations (in seconds)
PHASES = {
    "Red": {
        "duration": 2 * 60 * 60,  # 2 hours
        "color": "red",
        "states": [24 * 60, 24 * 60, 24 * 60, 23 * 60, 23 * 60],  # States in seconds
    },
    "Green": {
        "duration": 60 * 60,  # 1 hour
        "color": "green",
        "states": [12 * 60, 11 * 60, 11 * 60, 11 * 60, 11 * 60],
    },
    "Black": {
        "duration": 5 * 60,  # 5 minutes
        "color": "black",
        "states": [60, 60, 60, 60, 60],  # Each state lasts 1 minute
    },
}

# Load saved state from file
def load_state():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return None

# Save state to file (Only called when manually setting or resetting)
def save_state(init_time, phase, state):
    data = {"init_time": init_time, "phase": phase, "state": state}
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)
    print(f"Saved state: {data}")  # Debugging output

# Reset confirmation and action
def reset():
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset?"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        initialize_tracker()

# Initialize tracker at the current time
def initialize_tracker():
    global init_time, current_phase, current_state
    init_time = time.time()
    current_phase = "Red"
    current_state = 5
    save_state(init_time, current_phase, current_state)
    update_display()

# Calculate the current phase and state based on elapsed time
def update_state():
    global current_phase, current_state
    elapsed_time = time.time() - init_time

    for phase, data in PHASES.items():
        if elapsed_time < data["duration"]:
            cumulative_time = 0

            for i, state_duration in enumerate(data["states"], start=1):
                cumulative_time += state_duration
                if elapsed_time < cumulative_time:
                    current_phase = phase
                    current_state = 6 - i  # Reverse order for display
                    return
        elapsed_time -= data["duration"]

    # Loop back to Red after Black ends
    initialize_tracker()

# Manually set phase and state
def set_manual_state():
    global init_time, current_phase, current_state

    selected_phase = phase_var.get()
    selected_state = int(state_var.get())

    if selected_phase and selected_state:
        current_phase = selected_phase
        current_state = selected_state

        # Calculate how much time has passed in the phase BEFORE this state
        elapsed_time_in_phase = sum(PHASES[selected_phase]["states"][:5 - selected_state])  # Reverse order
        remaining_time_in_phase = PHASES[selected_phase]["duration"] - (elapsed_time_in_phase * 60)

        # Set init_time so that we are at the start of the selected state
        init_time = time.time() - (PHASES[selected_phase]["duration"] - remaining_time_in_phase)

        # **Fix: Save phase and state correctly in JSON file**
        save_state(init_time, current_phase, current_state)

        # **Force UI to update immediately without overwriting JSON again**
        update_display()

# Update the UI dynamically (DOES NOT SAVE STATE AUTOMATICALLY)
def update_display():
    update_state()
    remaining_time = PHASES[current_phase]["duration"] - (time.time() - init_time)
    remaining_phase = str(timedelta(seconds=int(remaining_time)))

    phase_label.config(text=f"Phase: {current_phase}", fg=PHASES[current_phase]["color"])
    state_label.config(text=f"State: {current_state}")
    time_label.config(text=f"Time Remaining: {remaining_phase}")

    root.after(1000, update_display)  # Refresh every second

# Create UI
root = tk.Tk()
root.title("Event Tracker")
root.geometry("400x250")

# Labels
phase_label = tk.Label(root, text="", font=("Arial", 16))
phase_label.pack(pady=10)

state_label = tk.Label(root, text="", font=("Arial", 14))
state_label.pack(pady=5)

time_label = tk.Label(root, text="", font=("Arial", 14))
time_label.pack(pady=5)

# Frame to hold manual phase selection options in one row
manual_frame = tk.Frame(root)
manual_frame.pack(pady=10)

# Dropdown for selecting phase
phase_var = tk.StringVar(root)
phase_var.set("Red")  # Default value
phase_dropdown = tk.OptionMenu(manual_frame, phase_var, *PHASES.keys())
phase_dropdown.grid(row=0, column=0, padx=5)

# Dropdown for selecting state (Descending order)
state_var = tk.StringVar(root)
state_var.set("5")  # Default value
state_dropdown = tk.OptionMenu(manual_frame, state_var, "5", "4", "3", "2", "1")
state_dropdown.grid(row=0, column=1, padx=5)

# Button to manually set the phase and state
manual_set_button = tk.Button(manual_frame, text="Set", command=set_manual_state, bg="blue", fg="white")
manual_set_button.grid(row=0, column=2, padx=5)

# Reset button (Now below other controls)
reset_button = tk.Button(root, text="Reset", command=reset, bg="gray", fg="white")
reset_button.pack(pady=20)

# Load saved state or initialize new tracking
saved_state = load_state()
if saved_state:
    init_time = saved_state["init_time"]
    current_phase = saved_state["phase"]
    current_state = saved_state["state"]
else:
    initialize_tracker()

update_display()  # Start UI update loop
root.mainloop()
