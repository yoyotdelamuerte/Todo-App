import unittest
from unittest.mock import patch, mock_open
import tkinter as tk
from main import TodoApp
from xmlrunner import XMLTestRunner


class TestTodoApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = TodoApp(self.root)
        self.app.task_list = []  # Ensure task list is empty
        self.app.completed_tasks = []  # Ensure completed tasks list is empty

    def tearDown(self):
        self.root.destroy()

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_add_task(self, mock_open):
        # Test adding a new task
        self.app.task_entry.insert(0, "Test Task")
        self.app.add_task()
        self.assertIn("Test Task", self.app.task_list)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_delete_task(self, mock_open):
        # Test deleting an existing task
        self.app.load_tasks()
        self.app.load_tasks_in_frame()
        self.app.delete_task("Test Task")
        self.assertNotIn("Test Task", self.app.task_list)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_edit_task(self, mock_open):
        # Test editing an existing task
        self.app.load_tasks()
        self.app.load_tasks_in_frame()

        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Test Task")

        self.assertIn("Edited Task", self.app.task_list)
        self.assertNotIn("Test Task", self.app.task_list)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_toggle_task_completion(self, mock_open):
        # Test toggling the completion status of a task
        self.app.load_tasks()
        self.app.load_tasks_in_frame()
        self.app.toggle_task_completion("Test Task")
        self.assertIn("Test Task", self.app.completed_tasks)
        self.assertNotIn("Test Task", self.app.task_list)
        self.app.toggle_task_completion("Test Task")
        self.assertIn("Test Task", self.app.task_list)
        self.assertNotIn("Test Task", self.app.completed_tasks)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_mark_task_completed(self, mock_open):
        # Test marking a task as completed
        self.app.load_tasks()
        self.app.load_tasks_in_frame()
        self.app.toggle_task_completion("Test Task")
        self.assertIn("Test Task", self.app.completed_tasks)
        self.assertNotIn("Test Task", self.app.task_list)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,completed\n")
    def test_unmark_task_completed(self, mock_open):
        # Test unmarking a task as completed
        self.app.load_tasks()
        self.app.load_tasks_in_frame()
        self.app.toggle_task_completion("Test Task")
        self.assertIn("Test Task", self.app.task_list)
        self.assertNotIn("Test Task", self.app.completed_tasks)

    @patch('main.messagebox.showwarning')
    @patch('main.open', new_callable=mock_open, read_data="")
    def test_add_empty_task(self, mock_open, mock_messagebox):
        # Test adding an empty task
        self.app.task_entry.insert(0, "")
        self.app.add_task()
        mock_messagebox.assert_called_with("Warning", "You must enter a task.")
        self.assertEqual(len(self.app.task_list), 0)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_delete_nonexistent_task(self, mock_open):
        # Test deleting a nonexistent task
        self.app.delete_task("Nonexistent Task")
        self.assertEqual(len(self.app.task_list), 0)
        self.assertEqual(len(self.app.completed_tasks), 0)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_initial_state(self, mock_open):
        # Test initial state of task lists
        self.assertEqual(len(self.app.task_list), 0)
        self.assertEqual(len(self.app.completed_tasks), 0)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_persistence_of_tasks(self, mock_open):
        # Test loading tasks from file
        self.app.load_tasks()
        self.assertIn("Test Task", self.app.task_list)
        self.assertEqual(len(self.app.task_list), 1)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_task_counters(self, mock_open):
        # Test updating task counters
        self.app.task_entry.insert(0, "Task 1")
        self.app.add_task()
        self.app.task_entry.insert(0, "Task 2")
        self.app.add_task()
        self.app.toggle_task_completion("Task 1")
        pending_text = self.app.pending_title.cget("text")
        resolved_text = self.app.completed_title.cget("text")
        self.assertIn("Pending Tasks (1)", pending_text)
        self.assertIn("Resolved Tasks (1)", resolved_text)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_edit_nonexistent_task(self, mock_open):
        # Test editing a nonexistent task
        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Nonexistent Task")
        self.assertEqual(len(self.app.task_list), 0)
        self.assertEqual(len(self.app.completed_tasks), 0)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_edit_task_text(self, mock_open):
        # Test editing the text of a task
        self.app.load_tasks()
        self.app.load_tasks_in_frame()

        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Test Task")

        self.assertIn("Edited Task", self.app.task_list)
        self.assertNotIn("Test Task", self.app.task_list)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_edit_task_status_unchanged(self, mock_open):
        # Test that editing a task does not change its completion status
        self.app.load_tasks()
        self.app.load_tasks_in_frame()

        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Test Task")

        self.assertIn("Edited Task", self.app.task_list)
        self.assertEqual(len(self.app.completed_tasks), 0)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_interface_update_on_add(self, mock_open):
        # Test that the interface updates correctly when a task is added
        self.app.task_entry.insert(0, "Test Task")
        self.app.add_task()
        task_frames = self.app.tasks_frame.winfo_children()
        task_labels = [frame.winfo_children()[1].cget("text") for frame in task_frames if isinstance(frame, tk.Frame)]
        self.assertIn("Test Task", task_labels)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_interface_update_on_delete(self, mock_open):
        # Test that the interface updates correctly when a task is deleted
        self.app.load_tasks()
        self.app.load_tasks_in_frame()
        self.app.delete_task("Test Task")
        task_frames = self.app.tasks_frame.winfo_children()
        task_labels = [frame.winfo_children()[1].cget("text") for frame in task_frames if isinstance(frame, tk.Frame)]
        self.assertNotIn("Test Task", task_labels)

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_save_tasks_on_add(self, mock_open):
        # Test that tasks are correctly saved when a task is added
        self.app.task_entry.insert(0, "Test Task")
        self.app.add_task()
        mock_open.assert_called_with(self.app.file_name, 'w')
        handle = mock_open()
        handle.write.assert_any_call("Test Task,pending\n")

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_save_tasks_on_delete(self, mock_open):
        # Test that tasks are correctly saved when a task is deleted
        self.app.task_list.append("Test Task")
        self.app.save_tasks()
        mock_open.assert_called_with(self.app.file_name, 'w')
        handle = mock_open()
        handle.write.assert_any_call("Test Task,pending\n")
        self.app.delete_task("Test Task")
        self.app.save_tasks()
        # Check if the specific write call with "Test Task,pending\n" is not in the mock calls
        write_calls = handle().write.call_args_list
        self.assertNotIn(("Test Task,pending\n",), [call[0] for call in write_calls])

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_switch_language_to_french(self, mock_open):
        # Test switching the application language to French
        self.app.set_language("fr")
        self.assertEqual(self.app.current_language, "fr")
        self.assertEqual(self.app.add_task_button.cget("text"), "Ajouter Tâche")
        self.assertIn("Tâches en attente", self.app.pending_title.cget("text"))
        self.assertIn("Tâches résolues", self.app.completed_title.cget("text"))

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_switch_language_to_spanish(self, mock_open):
        # Test switching the application language to Spanish
        self.app.set_language("es")
        self.assertEqual(self.app.current_language, "es")
        self.assertEqual(self.app.add_task_button.cget("text"), "Añadir tarea")
        self.assertIn("Tareas pendientes", self.app.pending_title.cget("text"))
        self.assertIn("Tareas resueltas", self.app.completed_title.cget("text"))

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_switch_language_to_italian(self, mock_open):
        # Test switching the application language to Italian
        self.app.set_language("it")
        self.assertEqual(self.app.current_language, "it")
        self.assertEqual(self.app.add_task_button.cget("text"), "Aggiungi compito")
        self.assertIn("Compiti in sospeso", self.app.pending_title.cget("text"))
        self.assertIn("Compiti risolti", self.app.completed_title.cget("text"))

    @patch('main.open', new_callable=mock_open, read_data="")
    def test_switch_language_to_german(self, mock_open):
        # Test switching the application language to German
        self.app.set_language("de")
        self.assertEqual(self.app.current_language, "de")
        self.assertEqual(self.app.add_task_button.cget("text"), "Aufgabe hinzufügen")
        self.assertIn("Ausstehende Aufgaben", self.app.pending_title.cget("text"))
        self.assertIn("Erledigte Aufgaben", self.app.completed_title.cget("text"))

    @patch('main.open', new_callable=mock_open, read_data="Test Task,pending\n")
    def test_task_remains_in_pending_when_editing(self, mock_open):
        # Test that a task remains in the pending list when edited
        self.app.load_tasks()
        self.app.load_tasks_in_frame()

        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Test Task")

        self.assertIn("Edited Task", self.app.task_list)
        self.assertNotIn("Test Task", self.app.task_list)
        self.assertEqual(len(self.app.completed_tasks), 0)

    @patch('main.open', new_callable=mock_open, read_data="Test Task,completed\n")
    def test_task_remains_in_completed_when_editing(self, mock_open):
        # Test that a task remains in the completed list when edited
        self.app.load_tasks()
        self.app.load_tasks_in_frame()

        with patch('tkinter.simpledialog.askstring', return_value="Edited Task"):
            self.app.edit_task("Test Task")

        self.assertIn("Edited Task", self.app.completed_tasks)
        self.assertNotIn("Test Task", self.app.completed_tasks)
        self.assertEqual(len(self.app.task_list), 0)


if __name__ == "__main__":
    with open('test-reports.xml', 'wb') as output:
        unittest.main(testRunner=XMLTestRunner(output=output))
