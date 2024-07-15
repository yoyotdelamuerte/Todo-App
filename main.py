import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, Menu
import os
import unittest
from io import BytesIO
from unittest.mock import patch, mock_open
from xmlrunner import XMLTestRunner
import xml.etree.ElementTree as ET


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo App")
        self.task_list = []
        self.completed_tasks = []
        self.file_name = "tasks.txt"
        self.current_language = "en"

        self.initialize_file()
        self.load_tasks()

        self.create_menu()

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.task_entry = tk.Entry(self.frame, width=30)
        self.task_entry.grid(row=0, column=0)

        self.add_task_button = tk.Button(self.frame, text="Add Task", command=self.add_task, bg="green", fg="white")
        self.add_task_button.grid(row=0, column=1)

        self.pending_title = tk.Label(self.frame, text="Pending Tasks", fg="blue")
        self.pending_title.grid(row=1, column=0, columnspan=2)

        self.tasks_frame = tk.Frame(self.frame)
        self.tasks_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.completed_title = tk.Label(self.frame, text="Resolved Tasks", fg="green")
        self.completed_title.grid(row=3, column=0, columnspan=2)

        self.completed_frame = tk.Frame(self.frame)
        self.completed_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.update_task_counter()

        self.load_tasks_in_frame()

    def create_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)

        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=file_menu)
        file_menu.add_command(label="Run Tests", command=self.run_tests)
        file_menu.add_separator()
        language_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Language", menu=language_menu)
        language_menu.add_command(label="English", command=lambda: self.set_language("en"))
        language_menu.add_command(label="French", command=lambda: self.set_language("fr"))
        language_menu.add_command(label="Spanish", command=lambda: self.set_language("es"))
        language_menu.add_command(label="Italian", command=lambda: self.set_language("it"))
        language_menu.add_command(label="German", command=lambda: self.set_language("de"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def initialize_file(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as file:
                pass

    def load_tasks(self):
        with open(self.file_name, "r") as file:
            for line in file:
                parts = line.strip().rsplit(',', 1)
                if len(parts) == 2:
                    task, status = parts
                    if status == 'completed':
                        self.completed_tasks.append(task)
                    else:
                        self.task_list.append(task)

    def save_tasks(self):
        with open(self.file_name, "w") as file:
            for task in self.task_list:
                file.write(f"{task},pending\n")
            for task in self.completed_tasks:
                file.write(f"{task},completed\n")

    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.task_list.insert(0, task)
            self.save_tasks()
            self.load_tasks_in_frame()
            self.update_task_counter()
            self.task_entry.delete(0, tk.END)
        else:
            self.show_warning("You must enter a task.")

    def load_tasks_in_frame(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        for widget in self.completed_frame.winfo_children():
            widget.destroy()

        for task in self.task_list:
            self.create_task_frame(self.tasks_frame, task, completed=False)

        for task in self.completed_tasks:
            self.create_task_frame(self.completed_frame, task, completed=True)

        self.update_task_counter()

    def create_task_frame(self, parent_frame, task, completed=False):
        task_frame = tk.Frame(parent_frame, pady=2)
        task_frame.pack(fill='x', padx=5, pady=2)

        task_var = tk.StringVar(value=task)

        task_check = tk.Checkbutton(task_frame, variable=task_var, onvalue=task, offvalue="",
                                    command=lambda t=task: self.toggle_task_completion(t))
        task_check.pack(side='left')

        task_label = tk.Label(task_frame, text=task)
        if completed:
            task_label.config(fg="gray", font=("Helvetica", 10, "italic"))
            task_check.select()
        task_label.pack(side='left', padx=5)

        button_frame = tk.Frame(task_frame)
        button_frame.pack(side='right')

        task_edit_button = tk.Button(button_frame, text=self.get_translation("Edit"), command=lambda t=task: self.edit_task(t), bg="green", fg="white")
        task_edit_button.pack(side='right', padx=5)

        task_delete_button = tk.Button(button_frame, text=self.get_translation("Delete"), command=lambda t=task: self.delete_task(t), bg="red", fg="white")
        task_delete_button.pack(side='right', padx=5)

        separator = ttk.Separator(parent_frame, orient='horizontal')
        separator.pack(fill='x', padx=5, pady=2)

    def toggle_task_completion(self, task):
        if task in self.task_list:
            self.task_list.remove(task)
            self.completed_tasks.append(task)
        elif task in self.completed_tasks:
            self.completed_tasks.remove(task)
            self.task_list.insert(0, task)
        self.save_tasks()
        self.load_tasks_in_frame()
        self.update_task_counter()

    def delete_task(self, task):
        if task in self.task_list:
            self.task_list.remove(task)
        elif task in self.completed_tasks:
            self.completed_tasks.remove(task)
        self.save_tasks()
        self.load_tasks_in_frame()
        self.update_task_counter()

    def edit_task(self, task):
        new_task = simpledialog.askstring(self.get_translation("Edit Task"), self.get_translation("Edit the task:"), initialvalue=task)

        if new_task:
            if task in self.task_list:
                index = self.task_list.index(task)
                self.task_list[index] = new_task
            elif task in self.completed_tasks:
                index = self.completed_tasks.index(task)
                self.completed_tasks[index] = new_task
            self.save_tasks()
            self.load_tasks_in_frame()

    def update_task_counter(self):
        pending_count = len(self.task_list)
        resolved_count = len(self.completed_tasks)
        self.pending_title.config(text=self.get_translation("Pending Tasks") + f" ({pending_count})")
        self.completed_title.config(text=self.get_translation("Resolved Tasks") + f" ({resolved_count})")

    def run_tests(self):
        test_output = BytesIO()
        runner = XMLTestRunner(output=test_output)

        suite = unittest.TestLoader().loadTestsFromModule(__import__('test_main'))

        runner.run(suite)

        test_output.seek(0)
        test_results = test_output.read().decode('utf-8')

        self.display_test_results(test_results)

    def display_test_results(self, test_results):
        root = ET.fromstring(test_results)

        results_window = tk.Toplevel(self.root)
        results_window.title("Test Results")

        results_text = tk.Text(results_window, wrap='word')

        for testsuite in root.findall('testsuite'):
            suite_name = testsuite.get('name')
            total_tests = testsuite.get('tests')
            failures = testsuite.get('failures')
            errors = testsuite.get('errors')
            skipped = testsuite.get('skipped')
            time = testsuite.get('time')

            results_text.insert(tk.END, f"Test Suite: {suite_name}\n")
            results_text.insert(tk.END,
                                f"Total Tests: {total_tests}, Failures: {failures}, Errors: {errors}, Skipped: {skipped}, Time: {time}s\n\n")

            for testcase in testsuite.findall('testcase'):
                classname = testcase.get('classname')
                name = testcase.get('name')
                time = testcase.get('time')

                results_text.insert(tk.END, f"Test Case: {name} ({classname}) - Time: {time}s\n")

                failure = testcase.find('failure')
                if failure is not None:
                    message = failure.get('message')
                    results_text.insert(tk.END, f"  FAILURE: {message}\n")

                error = testcase.find('error')
                if error is not None:
                    message = error.get('message')
                    results_text.insert(tk.END, f"  ERROR: {message}\n")

                results_text.insert(tk.END, "\n")

        results_text.config(state=tk.DISABLED)
        results_text.pack(expand=True, fill='both')

    def set_language(self, language):
        self.current_language = language
        self.update_language()

    def update_language(self):
        self.add_task_button.config(text=self.get_translation("Add Task"))
        self.pending_title.config(text=self.get_translation("Pending Tasks") + f" ({len(self.task_list)})")
        self.completed_title.config(text=self.get_translation("Resolved Tasks") + f" ({len(self.completed_tasks)})")
        self.load_tasks_in_frame()

    def get_translation(self, text):
        translations = {
            "en": {
                "Add Task": "Add Task",
                "Edit": "Edit",
                "Delete": "Delete",
                "Pending Tasks": "Pending Tasks",
                "Resolved Tasks": "Resolved Tasks",
                "Edit Task": "Edit Task",
                "Edit the task:": "Edit the task:",
                "You must enter a task.": "You must enter a task."
            },
            "fr": {
                "Add Task": "Ajouter Tâche",
                "Edit": "Modifier",
                "Delete": "Supprimer",
                "Pending Tasks": "Tâches en attente",
                "Resolved Tasks": "Tâches résolues",
                "Edit Task": "Modifier la tâche",
                "Edit the task:": "Modifiez la tâche:",
                "You must enter a task.": "Vous devez entrer une tâche."
            },
            "es": {
                "Add Task": "Añadir tarea",
                "Edit": "Editar",
                "Delete": "Eliminar",
                "Pending Tasks": "Tareas pendientes",
                "Resolved Tasks": "Tareas resueltas",
                "Edit Task": "Editar tarea",
                "Edit the task:": "Edita la tarea:",
                "You must enter a task.": "Debes ingresar una tarea."
            },
            "it": {
                "Add Task": "Aggiungi compito",
                "Edit": "Modifica",
                "Delete": "Elimina",
                "Pending Tasks": "Compiti in sospeso",
                "Resolved Tasks": "Compiti risolti",
                "Edit Task": "Modifica compito",
                "Edit the task:": "Modifica il compito:",
                "You must enter a task.": "Devi inserire un compito."
            },
            "de": {
                "Add Task": "Aufgabe hinzufügen",
                "Edit": "Bearbeiten",
                "Delete": "Löschen",
                "Pending Tasks": "Ausstehende Aufgaben",
                "Resolved Tasks": "Erledigte Aufgaben",
                "Edit Task": "Aufgabe bearbeiten",
                "Edit the task:": "Bearbeiten Sie die Aufgabe:",
                "You must enter a task.": "Sie müssen eine Aufgabe eingeben."
            }
        }
        return translations[self.current_language].get(text, text)

    def show_warning(self, message):
        messagebox.showwarning(self.get_translation("Warning"), self.get_translation(message))


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
