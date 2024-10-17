import tkinter as tk
from tkinter import messagebox
from trading_bot import TradingBot  # Ensure this is correctly importing your TradingBot class

class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot Control Panel")
        self.root.geometry("400x300")  # Set window size

        # Initialize the trading bot with a starting budget (e.g., $10000)
        self.bot = TradingBot(initial_budget=10000)

        # Create a frame for the budget display
        budget_frame = tk.Frame(root, padx=10, pady=10)
        budget_frame.grid(row=0, column=0, sticky="ew")

        # Label for the current budget
        self.budget_label = tk.Label(budget_frame, text=f"Current Budget: ${self.bot.current_budget}", font=("Arial", 14))
        self.budget_label.pack(fill="x", pady=5)

        # Frame for control buttons
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.grid(row=1, column=0, sticky="ew")

        # Start button
        self.start_button = tk.Button(control_frame, text="Start Bot", command=self.start_bot, bg="green", fg="white", font=("Arial", 12))
        self.start_button.pack(fill="x", pady=5)

        # Stop button
        self.stop_button = tk.Button(control_frame, text="Stop Bot", command=self.stop_bot, bg="red", fg="white", font=("Arial", 12))
        self.stop_button.pack(fill="x", pady=5)

        # Status frame and label
        status_frame = tk.Frame(root, padx=10, pady=10)
        status_frame.grid(row=2, column=0, sticky="ew")
        self.status_label = tk.Label(status_frame, text="Status: Idle", fg="green", font=("Arial", 12))
        self.status_label.pack(fill="x", pady=10)

    def start_bot(self):
        """Start the bot's trading loop."""
        self.status_label.config(text="Status: Running", fg="blue")
        self.bot.run_cycle()
        self.update_budget()

    def stop_bot(self):
        """Stop the bot (placeholder for actual stop functionality)."""
        self.status_label.config(text="Status: Stopped", fg="red")
        messagebox.showinfo("Trading Bot", "The bot has been stopped.")

    def update_budget(self):
        """Update the current budget display after running the bot."""
        self.budget_label.config(text=f"Current Budget: ${self.bot.current_budget}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
