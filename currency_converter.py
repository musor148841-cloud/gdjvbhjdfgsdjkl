import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # API configuration (free tier from exchangerate-api.com)
        self.api_key = "YOUR_API_KEY"  # Замените на реальный ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"

        # Load available currencies
        self.currencies = self.get_currencies()
        if not self.currencies:
            messagebox.showerror("Error", "Failed to load currencies. Check API key.")
            self.root.destroy()
            return

        # UI Elements
        self.create_widgets()

        # Load history from file
        self.history = self.load_history()
        self.update_history_table()

    def get_currencies(self):
        """Fetch list of available currencies from API"""
        try:
            url = f"{self.base_url}/{self.api_key}/codes"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data['result'] == 'success':
                # Return list of currency codes (e.g., ['USD', 'EUR', ...])
                return [code for code, name in data['supported_codes']]
            else:
                return []
        except Exception as e:
            print(f"Error fetching currencies: {e}")
            return ['USD', 'EUR', 'GBP', 'JPY', 'UAH']  # fallback

    def create_widgets(self):
        # Frame for conversion
        frame = ttk.LabelFrame(self.root, text="Currency Conversion", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        # From currency
        ttk.Label(frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_currency = ttk.Combobox(frame, values=self.currencies, width=10)
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        self.from_currency.set("USD")

        # To currency
        ttk.Label(frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.to_currency = ttk.Combobox(frame, values=self.currencies, width=10)
        self.to_currency.grid(row=0, column=3, padx=5, pady=5)
        self.to_currency.set("EUR")

        # Amount
        ttk.Label(frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        # Convert button
        self.convert_btn = ttk.Button(frame, text="Convert", command=self.convert)
        self.convert_btn.grid(row=1, column=2, padx=5, pady=5)

        # Result label
        self.result_label = ttk.Label(frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=2, column=0, columnspan=4, pady=10)

        # History frame
        history_frame = ttk.LabelFrame(self.root, text="Conversion History", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview for history
        columns = ("Date", "From", "To", "Amount", "Result")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        self.history_tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons for history
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save History", command=self.save_history_to_file).pack(side="left", padx=5)

    def convert(self):
        """Perform conversion using API"""
        amount_str = self.amount_entry.get().strip()
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive number for amount.")
            return

        try:
            # API request
            url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}/{amount}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data['result'] == 'success':
                converted = data['conversion_result']
                rate = data['conversion_rate']
                result_text = f"{amount} {from_curr} = {converted:.2f} {to_curr} (Rate: {rate:.4f})"
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
                self.save_history_to_file()  # auto-save after each conversion
            else:
                messagebox.showerror("API Error", "Conversion failed. Check currency codes.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to API: {e}")

    def load_history(self):
        """Load history from JSON file"""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history_to_file(self):
        """Save current history to JSON file"""
        try:
            with open("history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def update_history_table(self):
        """Refresh displayed history table"""
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for entry in self.history[-20:]:  # show last 20 entries
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["from"],
                entry["to"],
                f"{entry['amount']:.2f}",
                f"{entry['result']:.2f}"
            ))

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all history?"):
            self.history = []
            self.update_history_table()
            self.save_history_to_file()
            self.result_label.config(text="History cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
