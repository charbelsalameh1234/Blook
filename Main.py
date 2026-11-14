import tkinter as tk
# ttk gives us nicer widgets (we use it for the dropdown menus)
# messagebox lets us show pop-up messages
from tkinter import ttk, messagebox
import random



# 1. DATA

# The subjects a student can choose from
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology",
            "Computer Science", "English", "French",
            "History", "Economics"]

# Build every time slot like "Monday - Evening".
# This loops over each day and each time of day.
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]
TIMES = ["Morning", "Afternoon", "Evening"]
SLOTS = [day + " - " + time for day in DAYS for time in TIMES]

# Fake students to swipe on. Each one is a dictionary.
students = [
    {"name": "Emma Wilson", "school": "Concordia University",
     "strong": "Mathematics", "weak": "English",
     "availability": ["Monday - Evening", "Wednesday - Afternoon"]},

    {"name": "Lucas Martin", "school": "Collège de Bois-de-Boulogne",
     "strong": "Physics", "weak": "Mathematics",
     "availability": ["Tuesday - Afternoon", "Thursday - Evening"]},

    {"name": "Sophia Chen", "school": "Université de Montréal",
     "strong": "Biology", "weak": "Chemistry",
     "availability": ["Monday - Evening", "Friday - Afternoon"]},

    {"name": "Noah Tremblay", "school": "Collège de Bois-de-Boulogne",
     "strong": "Computer Science", "weak": "Physics",
     "availability": ["Wednesday - Afternoon", "Thursday - Evening"]},

    {"name": "Olivia Brown", "school": "McGill University",
     "strong": "Economics", "weak": "French",
     "availability": ["Tuesday - Afternoon", "Friday - Afternoon"]},

    {"name": "Ethan Roy", "school": "Collège de Bois-de-Boulogne",
     "strong": "Chemistry", "weak": "Biology",
     "availability": ["Monday - Evening", "Thursday - Evening"]},
]

# Things the app remembers while it runs
me = None            # your profile (empty until you save it)
passed = []          # students you pressed "Pass" on
matches = []         # students you pressed "Match" on
current = None       # the student currently shown on screen
chat_history = {}    # student name -> list of chat messages



# 2. WINDOW AND PAGES


# Create the main window
root = tk.Tk()
root.title("Blook")
root.geometry("700x700")
root.configure(bg="#17171F")  # dark background

# The row of buttons at the top used to switch pages
menu = tk.Frame(root, bg="#17171F")
menu.pack(fill="x", pady=10)

# One frame (a "page") for each screen of the app
profile_page = tk.Frame(root, bg="#17171F")
discover_page = tk.Frame(root, bg="#17171F")
messages_page = tk.Frame(root, bg="#17171F")

# Keep the pages in a dictionary so we can find them by name
pages = {"profile": profile_page,
         "discover": discover_page,
         "messages": messages_page}


def show_page(name):
    """Hide every page, then show only the one we want."""
    for page in pages.values():
        page.pack_forget()
    pages[name].pack(fill="both", expand=True, padx=30)

    # Refresh the page's content when we arrive on it
    if name == "discover":
        show_student()
    if name == "messages":
        refresh_matches()


def go_to(name):
    """Called by the menu buttons. Blocks pages you can't use yet."""
    if name == "discover" and me is None:
        messagebox.showwarning("Oops", "Create your profile first.")
        return
    if name == "messages" and not matches:
        messagebox.showinfo("Oops", "Match with someone first.")
        return
    show_page(name)


# Create the three menu buttons
for name, text in [("profile", "My Profile"),
                   ("discover", "Discover"),
                   ("messages", "Messages")]:
    # "n=name" makes each button remember its own page name
    tk.Button(menu, text=text, bg="#873FEE", fg="white",
              relief="flat", padx=15, pady=8,
              command=lambda n=name: go_to(n)).pack(side="left", padx=10)


# Small helper so we don't repeat the same label code many times
def make_label(parent, text, size=11, color="white"):
    label = tk.Label(parent, text=text, bg="#17171F", fg=color,
                     font=("Arial", size), wraplength=600)
    label.pack(pady=4)
    return label



# 3. PROFILE PAGE


make_label(profile_page, "Build your profile", 20)

# Text boxes for name and school
make_label(profile_page, "Your name", 10, "#A1A1B0")
name_entry = tk.Entry(profile_page, width=40)
name_entry.pack()

make_label(profile_page, "Your school", 10, "#A1A1B0")
school_entry = tk.Entry(profile_page, width=40)
school_entry.pack()

# Dropdown menus for subjects ("readonly" = can't type your own)
make_label(profile_page, "Your strongest subject", 10, "#A1A1B0")
strong_box = ttk.Combobox(profile_page, values=SUBJECTS, state="readonly")
strong_box.pack()

make_label(profile_page, "Subject you need help with", 10, "#A1A1B0")
weak_box = ttk.Combobox(profile_page, values=SUBJECTS, state="readonly")
weak_box.pack()

# A list where you can click several time slots (MULTIPLE = more than one)
make_label(profile_page, "Your availability (click all that apply)",
           10, "#A1A1B0")
slot_list = tk.Listbox(profile_page, selectmode=tk.MULTIPLE,
                       height=8, exportselection=False)
slot_list.pack()
for slot in SLOTS:
    slot_list.insert(tk.END, slot)


def save_profile():
    """Check the form and save it into the 'me' variable."""
    global me  # we want to change the variable defined at the top

    name = name_entry.get().strip()      # .strip() removes extra spaces
    school = school_entry.get().strip()
    strong = strong_box.get()
    weak = weak_box.get()

    # curselection() gives the numbers of the selected rows;
    # we turn those numbers into the actual slot text
    availability = [SLOTS[i] for i in slot_list.curselection()]

    # Make sure everything is filled in
    if not (name and school and strong and weak and availability):
        messagebox.showerror("Missing info", "Please fill in everything.")
        return

    # Strong and weak subject must be different
    if strong == weak:
        messagebox.showerror("Oops", "Choose two different subjects.")
        return

    # Save the profile as a dictionary
    me = {"name": name, "school": school, "strong": strong,
          "weak": weak, "availability": availability}

    messagebox.showinfo("Saved", "Your profile is ready!")
    show_page("discover")


tk.Button(profile_page, text="Save Profile", bg="#873FEE", fg="white",
          relief="flat", padx=15, pady=8,
          command=save_profile).pack(pady=15)



# 4. COMPATIBILITY SCORE


def compatibility(student):
    """Give a score out of 100 and the list of shared time slots."""
    score = 0

    # +40 if they are strong in what you struggle with
    if student["strong"] == me["weak"]:
        score += 40

    # +40 if you are strong in what they struggle with
    if student["weak"] == me["strong"]:
        score += 40

    # Time slots that both of you picked (set & set = overlap)
    shared = set(me["availability"]) & set(student["availability"])

    # Up to +20 depending on how many of YOUR slots you share
    score += 20 * len(shared) / len(me["availability"])

    return round(score), sorted(shared)



# 5. DISCOVER PAGE


# Labels that will be filled in with the current student's info
make_label(discover_page, "Find your study match", 20)
student_name = make_label(discover_page, "", 18)
student_score = make_label(discover_page, "", 14, "#873FEE")
student_info = make_label(discover_page, "", 11, "#A1A1B0")
student_shared = make_label(discover_page, "", 11)


def show_student():
    """Find the next student you haven't seen and display them."""
    global current

    current = None
    # Look for the first student you haven't passed or matched with
    for s in students:
        if s not in passed and s not in matches:
            current = s
            break

    # Nobody left
    if current is None:
        student_name.config(text="You've seen everyone!")
        student_score.config(text="")
        student_info.config(text="")
        student_shared.config(text="")
        return

    # Otherwise show their info
    score, shared = compatibility(current)
    student_name.config(text=current["name"])
    student_score.config(text=str(score) + "% COMPATIBILITY")
    student_info.config(text=current["school"] + "\n\nStrong at: "
                        + current["strong"] + "\nNeeds help with: "
                        + current["weak"])
    student_shared.config(text="Shared times: "
                          + (", ".join(shared) if shared else "none"))


def pass_student():
    """Skip this student and show the next one."""
    if current is None:
        return
    passed.append(current)
    show_student()


def match_student():
    """Match with this student and open the chat."""
    if current is None:
        return
    matches.append(current)
    # Start their chat with a first message
    chat_history[current["name"]] = ["Blook: You matched with "
                                     + current["name"] + "!"]
    messagebox.showinfo("It's a match!", "You matched with "
                        + current["name"] + "!")
    show_page("messages")


# Pass and Match buttons
buttons = tk.Frame(discover_page, bg="#17171F")
buttons.pack(pady=20)
tk.Button(buttons, text="Pass", padx=20, pady=8,
          command=pass_student).pack(side="left", padx=10)
tk.Button(buttons, text="♥ Match", bg="#873FEE", fg="white", padx=20,
          pady=8, command=match_student).pack(side="left", padx=10)


# 6. MESSAGES PAGE

make_label(messages_page, "Your conversations", 20)

# Dropdown to choose which match you want to chat with
chat_selector = ttk.Combobox(messages_page, state="readonly")
chat_selector.pack(fill="x", pady=5)

# The big box where the conversation is shown
chat_box = tk.Text(messages_page, height=15, state="disabled", wrap="word")
chat_box.pack(fill="x", pady=10)

# Area for the "suggest a study time" buttons
time_buttons = tk.Frame(messages_page, bg="#17171F")
time_buttons.pack(fill="x")

# Where you type your message
message_entry = tk.Entry(messages_page)
message_entry.pack(fill="x", pady=8, ipady=6)


def selected_student():
    """Return the student chosen in the dropdown."""
    for s in matches:
        if s["name"] == chat_selector.get():
            return s
    return None


def refresh_matches():
    """Fill the dropdown with your matches."""
    chat_selector["values"] = [s["name"] for s in matches]
    # If nothing is selected yet, pick the first one
    if chat_selector.get() == "":
        chat_selector.current(0)
    show_chat()


def show_chat():
    """Display the chat history and the study-time buttons."""
    student = selected_student()
    if student is None:
        return

    # Rewrite the whole chat box (it must be "normal" to edit it)
    chat_box.config(state="normal")
    chat_box.delete("1.0", tk.END)
    for line in chat_history[student["name"]]:
        chat_box.insert(tk.END, line + "\n\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)  # scroll to the newest message

    # Remove the old time buttons, then make new ones
    for widget in time_buttons.winfo_children():
        widget.destroy()

    shared = set(me["availability"]) & set(student["availability"])
    for slot in sorted(shared):
        tk.Button(time_buttons, text=slot,
                  command=lambda s=slot: send(
                      "Would you like to study on " + s + "?")
                  ).pack(side="left", padx=3)


def send(message):
    """Add your message, plus a random reply from the other student."""
    student = selected_student()
    if student is None or not message:
        return

    history = chat_history[student["name"]]
    history.append(me["name"] + ": " + message)
    history.append(student["name"] + ": " + random.choice(
        ["Sounds good!", "I agree!", "That works for me.",
         "Let's study together!"]))
    show_chat()


def send_typed_message():
    """Send what you typed, then clear the text box."""
    send(message_entry.get().strip())
    message_entry.delete(0, tk.END)


tk.Button(messages_page, text="Send", bg="#873FEE", fg="white",
          command=send_typed_message).pack(anchor="e")

# Update the chat when you choose a different person in the dropdown
chat_selector.bind("<<ComboboxSelected>>", lambda event: show_chat())
# Pressing Enter also sends the message
message_entry.bind("<Return>", lambda event: send_typed_message())


# 7. START THE APP

show_page("profile")   # begin on the profile page
root.mainloop()        # keep the window open and listening for clicks