import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import random  # для демонстрации (в реальном приложении используются сохранённые курсы)

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter - Offline Mode")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Оффлайн-курсы валют (фиксированные для демо)
        self.rates_file = "exchange_rates.json"
        self.currencies = ['USD', 'EUR', 'UAH', 'GBP', 'JPY', 'CAD', 'CHF', 'CNY', 'PLN', 'TRY']
        
        # Загружаем сохранённые курсы или используем стандартные
        self.exchange_rates = self.load_rates()
        
        # Флаг интернета (для информативности)
        self.online_mode = self.check_connection()
        
        # UI Elements
        self.create_widgets()
        
        # Load history
        self.history = self.load_history()
        self.update_history_table()
        
        # Показываем статус
        self.update_status()

    def check_connection(self):
        """Проверка доступности интернета (опционально)"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def load_rates(self):
        """Загрузка курсов из файла или создание дефолтных"""
        if os.path.exists(self.rates_file):
            try:
                with open(self.rates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Проверяем, не устарели ли курсы (более 24 часов)
                    if datetime.now().timestamp() - data.get('timestamp', 0) < 86400:
                        return data['rates']
            except:
                pass
        
        # Дефолтные курсы (относительно USD)
        return {
            'USD': 1.0,
            'EUR': 0.92,
            'UAH': 41.2,
            'GBP': 0.79,
            'JPY': 150.5,
            'CAD': 1.37,
            'CHF': 0.91,
            'CNY': 7.24,
            'PLN': 4.02,
            'TRY': 32.1
        }

    def save_rates(self):
        """Сохранение курсов в файл"""
        data = {
            'timestamp': datetime.now().timestamp(),
            'rates': self.exchange_rates
        }
        with open(self.rates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def update_rates_online(self):
        """Обновление курсов из интернета (если есть соединение)"""
        if not self.online_mode:
            messagebox.showwarning("Offline Mode", 
                                 "No internet connection. Using cached exchange rates.\n"
                                 "You can manually edit rates in the 'Manual Rate' tab.")
            return
        
        try:
            import requests
            # Используем бесплатное API (без ключа, но с ограничениями)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if 'rates' in data:
                for currency in self.currencies:
                    if currency in data['rates']:
                        self.exchange_rates[currency] = data['rates'][currency]
                self.save_rates()
                messagebox.showinfo("Success", "Exchange rates updated successfully!")
                self.update_status()
                return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update rates: {str(e)}")
        return False

    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Converter
        self.converter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_tab, text="Converter")
        self.create_converter_tab()
        
        # Tab 2: Manual rates
        self.manual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_tab, text="Manual Rates")
        self.create_manual_tab()
        
        # Tab 3: History
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="History")
        self.create_history_tab()

    def create_converter_tab(self):
        # Status bar
        self.status_label = ttk.Label(self.converter_tab, text="", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        # Main frame
        main_frame = ttk.Frame(self.converter_tab, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # From currency
        ttk.Label(main_frame, text="From Currency:", font=("Arial", 10)).grid(row=0, column=0, pady=10, sticky='w')
        self.from_currency = ttk.Combobox(main_frame, values=self.currencies, width=15, font=("Arial", 10))
        self.from_currency.grid(row=0, column=1, pady=10, padx=10)
        self.from_currency.set("USD")
        
        # To currency
        ttk.Label(main_frame, text="To Currency:", font=("Arial", 10)).grid(row=1, column=0, pady=10, sticky='w')
        self.to_currency = ttk.Combobox(main_frame, values=self.currencies, width=15, font=("Arial", 10))
        self.to_currency.grid(row=1, column=1, pady=10, padx=10)
        self.to_currency.set("EUR")
        
        # Amount
        ttk.Label(main_frame, text="Amount:", font=("Arial", 10)).grid(row=2, column=0, pady=10, sticky='w')
        self.amount_entry = ttk.Entry(main_frame, width=20, font=("Arial", 10))
        self.amount_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.convert, width=20)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Result
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 14, "bold"), foreground="blue")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Info about current rates
        info_frame = ttk.LabelFrame(main_frame, text="Current Rates (vs USD)", padding=10)
        info_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky='ew')
        
        self.rates_text = tk.Text(info_frame, height=8, width=40, font=("Courier", 9))
        self.rates_text.pack()
        self.update_rates_display()

    def create_manual_tab(self):
        frame = ttk.Frame(self.manual_tab, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Manual Exchange Rate Editor", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(frame, text="Edit rates manually (1 USD = ?)", font=("Arial", 10)).pack()
        
        # Canvas for scrolling
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.rate_entries = {}
        for i, currency in enumerate(self.currencies):
            ttk.Label(scrollable_frame, text=f"{currency}:", width=10).grid(row=i, column=0, pady=5, padx=5)
            entry = ttk.Entry(scrollable_frame, width=15)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entry.insert(0, str(self.exchange_rates.get(currency, 1.0)))
            self.rate_entries[currency] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save Rates", command=self.save_manual_rates).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Online", command=self.update_rates_online).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=self.reset_rates).pack(side='left', padx=5)

    def create_history_tab(self):
        frame = ttk.Frame(self.history_tab, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ("Date", "From", "To", "Amount", "Result")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export History", command=self.export_history).pack(side='left', padx=5)

    def convert(self):
        """Perform conversion using local rates (offline)"""
        amount_str = self.amount_entry.get().strip()
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive number for amount.")
            return
        
        # Get rates
        if from_curr not in self.exchange_rates or to_curr not in self.exchange_rates:
            messagebox.showerror("Error", "Currency not supported")
            return
        
        # Convert: amount in USD -> target currency
        amount_in_usd = amount / self.exchange_rates[from_curr]
        converted = amount_in_usd * self.exchange_rates[to_curr]
        
        result_text = f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}"
        self.result_label.config(text=result_text)
        
        # Save to history
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": converted
        }
        self.history.append(history_entry)
        self.update_history_table()
        self.save_history_to_file()

    def save_manual_rates(self):
        """Save manually entered rates"""
        try:
            for currency, entry in self.rate_entries.items():
                value = float(entry.get())
                if value <= 0:
                    raise ValueError
                self.exchange_rates[currency] = value
            self.save_rates()
            self.update_rates_display()
            messagebox.showinfo("Success", "Exchange rates updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers for all rates")

    def reset_rates(self):
        """Reset to default rates"""
        self.exchange_rates = {
            'USD': 1.0, 'EUR': 0.92, 'UAH': 41.2, 'GBP': 0.79,
            'JPY': 150.5, 'CAD': 1.37, 'CHF': 0.91, 'CNY': 7.24,
            'PLN': 4.02, 'TRY': 32.1
        }
        self.save_rates()
        for currency, entry in self.rate_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.exchange_rates.get(currency, 1.0)))
        self.update_rates_display()
        messagebox.showinfo("Success", "Rates reset to default values")

    def update_rates_display(self):
        """Update the rates display in converter tab"""
        self.rates_text.delete(1.0, tk.END)
        for currency in self.currencies[:5]:  # Show first 5 for brevity
            rate = self.exchange_rates.get(currency, 1.0)
            self.rates_text.insert(tk.END, f"1 USD = {rate:.4f} {currency}\n")

    def update_status(self):
        """Update status bar"""
        if self.online_mode:
            self.status_label.config(text="✅ Online mode - You can update rates", foreground="green")
        else:
            self.status_label.config(text="⚠️ Offline mode - Using cached rates", foreground="orange")

    def load_history(self):
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history_to_file(self):
        try:
            with open("history.json", "w", encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def update_history_table(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for entry in reversed(self.history[-50:]):  # Show last 50, newest first
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["from"],
                entry["to"],
                f"{entry['amount']:.2f}",
                f"{entry['result']:.2f}"
            ))

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure?"):
            self.history = []
            self.update_history_table()
            self.save_history_to_file()

    def export_history(self):
        filename = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"History exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
