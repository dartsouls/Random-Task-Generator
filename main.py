import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
from datetime import datetime

# Файл для сохранения данных
DATA_FILE = "tasks.json"

# Предопределённые задачи
DEFAULT_TASKS = [
    ("Прочитать статью", "Учёба"),
    ("Сделать зарядку", "Спорт"),
    ("Написать отчёт", "Работа"),
    ("Выучить новые слова", "Учёба"),
    ("Пробежка", "Спорт"),
    ("Созвониться с клиентом", "Работа")
]

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("550x500")
        
        # Данные
        self.tasks = []      # список задач [(название, категория)]
        self.history = []    # история [(название, категория, время)]
        
        self.load_data()
        
        # Если задач нет, добавляем стандартные
        if not self.tasks:
            for task, cat in DEFAULT_TASKS:
                self.tasks.append([task, cat])
            self.save_data()
        
        self.setup_ui()
        self.refresh_history()
    
    def setup_ui(self):
        # === Блок генерации ===
        gen_frame = tk.LabelFrame(self.root, text="Генератор", padx=10, pady=10)
        gen_frame.pack(fill="x", padx=10, pady=5)
        
        self.gen_btn = tk.Button(gen_frame, text="🎲 Сгенерировать задачу", 
                                  command=self.generate_task, font=("Arial", 12))
        self.gen_btn.pack(pady=5)
        
        self.current_label = tk.Label(gen_frame, text="Текущая задача: ---", 
                                       font=("Arial", 11, "bold"), fg="blue")
        self.current_label.pack(pady=5)
        
        # === Блок добавления ===
        add_frame = tk.LabelFrame(self.root, text="Добавить задачу", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(add_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = tk.Entry(add_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar(value="Учёба")
        cat_menu = ttk.Combobox(add_frame, textvariable=self.category_var, 
                                 values=["Учёба", "Спорт", "Работа"], state="readonly")
        cat_menu.grid(row=1, column=1, padx=5, pady=5)
        
        add_btn = tk.Button(add_frame, text="➕ Добавить", command=self.add_task)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # === Блок фильтра ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтр", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(filter_frame, text="Категория:").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="Все")
        filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                    values=["Все", "Учёба", "Спорт", "Работа"], 
                                    state="readonly", width=15)
        filter_menu.pack(side="left", padx=5)
        filter_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())
        
        reset_btn = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        reset_btn.pack(side="left", padx=5)
        
        # === Блок истории ===
        history_frame = tk.LabelFrame(self.root, text="История", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.listbox = tk.Listbox(history_frame, height=12)
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(history_frame, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)
    
    def load_data(self):
        """Загружает данные из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.history = data.get("history", [])
            except:
                self.tasks = []
                self.history = []
    
    def save_data(self):
        """Сохраняет данные в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"tasks": self.tasks, "history": self.history}, f, ensure_ascii=False, indent=2)
    
    def add_task(self):
        """Добавляет новую задачу с проверкой"""
        name = self.task_entry.get().strip()
        cat = self.category_var.get()
        
        # Проверка на пустую строку
        if not name:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        # Проверка на дубликат
        if [name, cat] in self.tasks:
            messagebox.showerror("Ошибка", "Такая задача уже есть!")
            return
        
        self.tasks.append([name, cat])
        self.save_data()
        messagebox.showinfo("Успех", f"Задача '{name}' добавлена!")
        self.task_entry.delete(0, tk.END)
    
    def generate_task(self):
        """Выбирает случайную задачу и добавляет в историю"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Сначала добавьте хотя бы одну задачу!")
            return
        
        task, cat = random.choice(self.tasks)
        time_str = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        self.history.append([task, cat, time_str])
        self.save_data()
        
        self.current_label.config(text=f"✨ {task} ({cat}) ✨")
        self.refresh_history()
    
    def refresh_history(self):
        """Обновляет список истории с учётом фильтра"""
        self.listbox.delete(0, tk.END)
        
        filter_cat = self.filter_var.get()
        
        for task, cat, time_str in self.history:
            if filter_cat == "Все" or cat == filter_cat:
                self.listbox.insert(tk.END, f"[{time_str}] {task} ({cat})")
    
    def reset_filter(self):
        """Сбрасывает фильтр"""
        self.filter_var.set("Все")
        self.refresh_history()

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
