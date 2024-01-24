import tkinter as tk
from threading import Thread
import random

def long_running_task():
    # Задача, которая занимает много времени
    for i in range(5):
        import time
        time.sleep(1)
        print("Task", i)
    print("fin")

def run_task_in_thread():
    # Создаем и запускаем новый поток для выполнения задачи
    thread = Thread(target=long_running_task)
    thread.start()
    # Планируем обновление интерфейса после завершения задачи
    root.after(100, check_task_completion, thread)

def check_task_completion(thread):
    # Проверяем, завершился ли поток
    if not thread.is_alive():
        "выполняем какой-нибудь класс, переданный аргументом"
        print("Task completed")
    else:
        # Планируем новую проверку через 100 миллисекунд
        root.after(100, check_task_completion, thread)

def show_random_number():
    random_number = random.randint(1, 100)
    result_label.config(text=f"Random Number: {random_number}")

def on_button_click():
    print("Button clicked")
    run_task_in_thread()

root = tk.Tk()

button_run_task = tk.Button(root, text="Run Task", command=on_button_click)
button_run_task.pack()

button_show_random = tk.Button(root, text="Show Random Number", command=show_random_number)
button_show_random.pack()

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
