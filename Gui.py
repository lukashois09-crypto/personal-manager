import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, Entry, Button
import SQLite_db
import os


if  os.path.exists('personal.db'):
    print('DB exists')
else:
    print("DB doesn't exist. Initializing...")
    SQLite_db.create_table()
    SQLite_db.insert_sample()


database = SQLite_db


def on_tree_select(event):
    selected = tree.selection()
    if not selected:
        return

    user_id = tree.item(selected[0], "values")[0]
    result = SQLite_db.get_employee_details(user_id)

    if result:
        name_label.config(text=f"Name: {result[0]}")
        berufstitel_label.config(text=f"Berufstitel: {result[1]}")
        email_label.config(text=f"Email: {result[2]}")
        telefonnummer_label.config(text=f"Telefonnummer: {result[3]}")

def filter_employees(*args):
    search_term = search_var.get().lower()
    tree.delete(*tree.get_children())

    for row in SQLite_db.search_employees(search_term):
        tree.insert("", "end", values=row)

def refresh_treeview():
    tree.delete(*tree.get_children())
    for user in SQLite_db.get_employees_basic():
        tree.insert("", "end", values=user)

def open_add_user_window():
    popup = Toplevel(window)
    popup.title("Neuer Mitarbeiter")
    popup.geometry("300x250")
    popup.resizable(False, False)

    Label(popup, text="Name").pack()
    entry_name = Entry(popup)
    entry_name.pack(fill="x", padx=10)

    Label(popup, text="Email").pack()
    entry_email = Entry(popup)
    entry_email.pack(fill="x", padx=10)

    Label(popup, text="Telefonnummer").pack()
    entry_telefonnummer = Entry(popup)
    entry_telefonnummer.pack(fill="x", padx=10)

    Label(popup, text="Berufstitel").pack()
    entry_berufstitel = Entry(popup)
    entry_berufstitel.pack(fill="x", padx=10)

    def save_user():
        name = entry_name.get().strip()
        email = entry_email.get().strip()
        telefonnummer = entry_telefonnummer.get().strip()
        berufstitel = entry_berufstitel.get().strip()

        if not name:
            messagebox.showerror("Fehler", "Name darf nicht leer sein.")
            return

        SQLite_db.add_user(name, email, telefonnummer, berufstitel)

        popup.destroy()
        refresh_treeview()

    Button(popup, text="Speichern", command=save_user).pack(pady=10)

def get_selected_user_id():
    selected = tree.selection()  # get selected row(s)
    if not selected:
        return None
    return tree.item(selected[0])["values"][0]  # ID is assumed to be the first column

def delete_selected_user():
    user_id = get_selected_user_id()
    if not user_id:
        messagebox.showwarning("Hinweis", "Bitte zuerst einen Mitarbeiter auswählen.")
        return

    # Ask for confirmation
    confirm = messagebox.askyesno("Bestätigen", "Mitarbeiter wirklich löschen?")
    if confirm:
        SQLite_db.delete_user(user_id)  # remove from database
        refresh_treeview()              # reload Treeview

def edit_selected_user():
    user_id = get_selected_user_id()
    if not user_id:
        messagebox.showwarning("Hinweis", "Bitte zuerst einen Mitarbeiter auswählen.")
        return

    # Fetch current data from DB
    with database.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, email, telefonnummer, berufstitel FROM users WHERE id=?", (user_id,))
        result = cur.fetchone()
        if not result:
            messagebox.showerror("Fehler", "Mitarbeiter nicht gefunden.")
            return

    # Open popup window
    popup = Toplevel(window)
    popup.title("Mitarbeiter bearbeiten")
    popup.geometry("300x250")
    popup.resizable(False, False)

    Label(popup, text="Name").pack()
    entry_name = Entry(popup)
    entry_name.pack(fill="x", padx=10)
    entry_name.insert(0, result[0])

    Label(popup, text="Email").pack()
    entry_email = Entry(popup)
    entry_email.pack(fill="x", padx=10)
    entry_email.insert(0, result[1])

    Label(popup, text="Telefonnummer").pack()
    entry_telefonnummer = Entry(popup)
    entry_telefonnummer.pack(fill="x", padx=10)
    entry_telefonnummer.insert(0, result[2])

    Label(popup, text="Berufstitel").pack()
    entry_berufstitel = Entry(popup)
    entry_berufstitel.pack(fill="x", padx=10)
    entry_berufstitel.insert(0, result[3])

    def save_changes():
        name = entry_name.get().strip()
        email = entry_email.get().strip()
        telefonnummer = entry_telefonnummer.get().strip()
        berufstitel = entry_berufstitel.get().strip()

        if not name:
            messagebox.showerror("Fehler", "Name darf nicht leer sein.")
            return

        # Update database
        SQLite_db.update_user(user_id, name, email, telefonnummer, berufstitel)
        popup.destroy()
        refresh_treeview()

        name_label.config(text=f"Name: {name}")
        berufstitel_label.config(text=f"Berufstitel: {berufstitel}")
        email_label.config(text=f"Email: {email}")
        telefonnummer_label.config(text=f"Telefonnummer: {telefonnummer}")


    Button(popup, text="Speichern", command=save_changes).pack(pady=10)

window = tk.Tk()
window.resizable(width=True, height=True)
window.minsize(width=1000, height=800)
window.geometry('1000x600')
window.title('personal manager')
window.configure(background='lightblue')

# Grid configuration
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=0)
window.grid_columnconfigure(1, weight=1)

# Left frame
frame_left = tk.Frame(window, bg='grey', width=500)
frame_left.grid(row=0, column=0, sticky='ns')
frame_left.grid_propagate(False)
frame_left.grid_rowconfigure(0, weight=0)
frame_left.grid_rowconfigure(1, weight=1)
frame_left.grid_rowconfigure(2, weight=0)
frame_left.grid_columnconfigure(0, weight=1)
frame_left.grid_columnconfigure(1, weight=0)
frame_left.grid_columnconfigure(2, weight=0)

# Search label
search_label = tk.Label(frame_left, text="Search:", bg='grey', fg='white', font=('Arial', 12))
search_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)

# Search entry
search_var = tk.StringVar()
search_var.trace_add('write', filter_employees)
search_entry = tk.Entry(frame_left, textvariable=search_var, width=30)
search_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

tree = ttk.Treeview(frame_left, columns=('ID', 'Name', 'Berufstitel'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Name', text='Name')
tree.heading('Berufstitel', text='Berufstitel')
tree.column('ID', width=40, anchor='center')
tree.grid(row=1, column=0, columnspan=2, sticky='nsew')

scrollbar = ttk.Scrollbar(frame_left, orient='vertical', command=tree.yview)
scrollbar.grid(row=1, column=2, sticky='ns')
tree.configure(yscrollcommand=scrollbar.set)

refresh_treeview()

btn_add = tk.Button(frame_left, text="Mitarbeiter hinzufügen", command=open_add_user_window)
btn_delete = tk.Button(frame_left, text="Mitarbeiter löschen", command=delete_selected_user)
btn_edit = tk.Button(frame_left, text="Mitarbeiter bearbeiten", command=edit_selected_user)

btn_add.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
btn_delete.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
btn_edit.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

# Right frame
frame_right = tk.Frame(window, bg="#209599")
frame_right.grid(row=0, column=1, sticky='nsew')
frame_right.grid_rowconfigure(0, weight=1)
frame_right.grid_columnconfigure(0, weight=1)

# Labels for employee info
name_label = tk.Label(frame_right, text='Name: ', font=('Arial', 16), bg="#209599")
berufstitel_label = tk.Label(frame_right, text='Berufstitel: ', font=('Arial', 16), bg="#209599")
email_label = tk.Label(frame_right, text='Email: ', font=("Arial", 16), bg="#209599")
telefonnummer_label = tk.Label(frame_right, text='Telefonnummer: ', font=("Arial", 16), bg="#209599")

berufstitel_label.grid(row=1, column=0, sticky='nw', padx=20, pady=10)
name_label.grid(row=0, column=0, sticky='nw', padx=20, pady=10)
email_label.grid(row=2, column=0, sticky='nw', padx=20, pady=10)
telefonnummer_label.grid(row=3, column=0, sticky='nw', padx=20, pady=10)

# Function to update right panel

tree.bind('<<TreeviewSelect>>', on_tree_select)

window.mainloop()