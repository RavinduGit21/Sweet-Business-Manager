import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os
import json
import uuid
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk


class WatalappamBusinessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SMORE DESSERT BAR")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f5f5f5")
        # Dark mode state
        self.dark_mode = False
        self.light_theme = {
            "bg": "#f5f5f5",
            "fg": "black",
            "button_bg": "#4CAF50",
            "button_fg": "white",
            "tree_bg": "white",
            "tree_fg": "black",
        }
        self.dark_theme = {
            "bg": "#2d2d2d",
            "fg": "white",
            "button_bg": "#3d3d3d",
            "button_fg": "white",
            "tree_bg": "#1e1e1e",
            "tree_fg": "white",
        }
        # File paths
        self.price_file = "prices.json"
        self.excel_file = "watalappam_orders.xlsx"
        self.receipt_folder = "receipts/"
        if not os.path.exists(self.receipt_folder):
            os.makedirs(self.receipt_folder)
        # Load prices and initialize Excel file
        self.load_prices()
        if not os.path.exists(self.excel_file):
            df = pd.DataFrame(
                columns=[
                    "Order No",
                    "Date",
                    "Customer Name",
                    "Phone Number",
                    "Address",
                    "500g Quantity",
                    "1kg Quantity",
                    "Total",
                    "Status",
                ]
            )
            df.to_excel(self.excel_file, index=False)
        # Variables for form fields
        self.customer_name_var = tk.StringVar()
        self.phone_number_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.qty_500g_var = tk.StringVar(value="0")
        self.qty_1kg_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="0.00")
        self.status_var = tk.StringVar(value="Pending")
        self.selected_order = None
        # Recalculate total when quantity changes
        self.qty_500g_var.trace("w", self.calculate_total)
        self.qty_1kg_var.trace("w", self.calculate_total)
        # Create widgets
        self.create_widgets()
        # Apply custom styles
        self.apply_styles()

    def apply_styles(self):
        """Apply custom styles to buttons and other widgets."""
        style = ttk.Style()
        style.theme_use("clam")
        # Button style
        style.configure(
            "TButton",
            background=self.light_theme["button_bg"],
            foreground=self.light_theme["button_fg"],
            font=("Arial", 12),
            padding=10,
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "TButton",
            background=[("active", "#45a049"), ("pressed", "#3e8e41")],
        )
        # Treeview style
        style.configure(
            "Treeview",
            background=self.light_theme["tree_bg"],
            fieldbackground=self.light_theme["tree_bg"],
            foreground=self.light_theme["tree_fg"],
            font=("Arial", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12, "bold"),
        )

    def load_prices(self):
        """Load prices from JSON file."""
        if os.path.exists(self.price_file):
            with open(self.price_file, "r") as file:
                self.prices = json.load(file)
        else:
            self.prices = {"500g": 500, "1kg": 1000}
            self.save_prices()

    def save_prices(self):
        """Save prices to JSON file."""
        with open(self.price_file, "w") as file:
            json.dump(self.prices, file)

    def calculate_total(self, *args):
        """Calculate the total price based on quantities."""
        try:
            qty_500g = int(self.qty_500g_var.get() or 0)
            qty_1kg = int(self.qty_1kg_var.get() or 0)
            total = (qty_500g * self.prices["500g"]) + (qty_1kg * self.prices["1kg"])
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            self.total_var.set("0.00")

    def create_widgets(self):
        """Create all GUI widgets."""
        # Header Section with Logo
        header_frame = tk.Frame(self.root, bg="#4CAF50", pady=20)
        header_frame.pack(fill="x")

        # Add Logo
        try:
            logo_image = Image.open("logo.jpg")
            logo_image = logo_image.resize((50, 50))
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(header_frame, image=logo_photo, bg="#4CAF50")
            logo_label.image = logo_photo
            logo_label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Add Application Name
        app_name_label = tk.Label(
            header_frame,
            text="Watalappam Business Manager",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#4CAF50"
        )
        app_name_label.pack(side="left", padx=10)

        # Add ? Button for Developer Information
        self.info_button = tk.Button(
            header_frame,
            text="?",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.show_developer_info,
            relief="flat",
            width=3,
            height=1,
            bd=0,
            highlightthickness=0,
        )
        self.info_button.pack(side="right", padx=10)

        # Frame for top-right buttons (Clear Form and Dark Mode)
        top_button_frame = tk.Frame(self.root, bg=self.light_theme["bg"])
        top_button_frame.pack(anchor="ne", padx=10, pady=10)

        # Clear Form button
        self.clear_form_button = ttk.Button(
            top_button_frame, text="Clear Form", command=self.clear_form, style="TButton"
        )
        self.clear_form_button.pack(side="left", padx=5)

        # Dark mode button
        self.dark_mode_button = ttk.Button(
            top_button_frame, text="🌙", command=self.toggle_dark_mode, style="TButton"
        )
        self.dark_mode_button.pack(side="left", padx=5)

        # Report Button
        self.report_button = ttk.Button(
            top_button_frame,
            text="📊 Report",
            command=self.open_report_dashboard,
            style="TButton",
        )
        self.report_button.pack(side="left", padx=5)

        # Receipt Button
        self.receipt_button = ttk.Button(
            top_button_frame,
            text="🖨️ Receipt",
            command=self.generate_receipt,
            style="TButton",
        )
        self.receipt_button.pack(side="left", padx=5)

        # Main form frame
        frame = tk.Frame(self.root, bg=self.light_theme["bg"], padx=20, pady=20)
        frame.pack()

        # Left side fields: Customer Name, 500g Quantity, 1kg Quantity, Order Status
        ttk.Label(
            frame,
            text="Customer Name:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.customer_name_var, font=("Arial", 12)).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Label(
            frame,
            text="500g Quantity:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.qty_500g_var, font=("Arial", 12)).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Label(
            frame,
            text="1kg Quantity:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.qty_1kg_var, font=("Arial", 12)).grid(
            row=2, column=1, padx=5, pady=5
        )
        ttk.Label(
            frame,
            text="Order Status:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        status_combobox = ttk.Combobox(
            frame,
            textvariable=self.status_var,
            values=["Pending", "In Progress", "Completed"],
            font=("Arial", 12),
        )
        status_combobox.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(
            frame,
            text="Total (Rs):",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(
            frame,
            textvariable=self.total_var,
            font=("Arial", 12, "bold"),
            background=self.light_theme["bg"],
            foreground="blue",
        ).grid(row=4, column=1, padx=5, pady=5)

        # Right side fields: Phone Number, Address
        ttk.Label(
            frame,
            text="Phone Number:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.phone_number_var, font=("Arial", 12)).grid(
            row=0, column=3, padx=5, pady=5
        )
        ttk.Label(
            frame,
            text="Address:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.address_var, font=("Arial", 12)).grid(
            row=1, column=3, padx=5, pady=5
        )

        # Date range filter
        ttk.Label(
            frame,
            text="Start Date:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.start_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.start_date_var, font=("Arial", 12)).grid(
            row=2, column=3, padx=5, pady=5
        )
        ttk.Label(
            frame,
            text="End Date:",
            background=self.light_theme["bg"],
            foreground=self.light_theme["fg"],
            font=("Arial", 12),
        ).grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.end_date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.end_date_var, font=("Arial", 12)).grid(
            row=3, column=3, padx=5, pady=5
        )

        # Filter and Reset buttons in the same row
        button_frame = tk.Frame(frame, bg=self.light_theme["bg"])
        button_frame.grid(row=4, column=2, columnspan=2, pady=10)
        ttk.Button(
            button_frame,
            text="Filter by Date",
            command=self.filter_orders_by_date,
            style="TButton",
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_date_filter,
            style="TButton",
        ).pack(side="left", padx=5)

        # Buttons
        button_frame = tk.Frame(self.root, bg=self.light_theme["bg"])
        button_frame.pack(pady=10, fill="x")
        # Center buttons frame
        center_buttons = tk.Frame(button_frame, bg=self.light_theme["bg"])
        center_buttons.pack(expand=True)
        # Right button frame
        right_buttons = tk.Frame(button_frame, bg=self.light_theme["bg"])
        right_buttons.pack(side="right", padx=20)
        # Center aligned buttons
        ttk.Button(
            center_buttons, text="Add Order", command=self.add_order, style="TButton"
        ).pack(side="left", padx=5)
        ttk.Button(
            center_buttons,
            text="Update Order",
            command=self.update_order,
            style="TButton",
        ).pack(side="left", padx=5)
        # Right aligned buttons
        ttk.Button(
            right_buttons,
            text="Delete Order",
            command=self.delete_order,
            style="TButton",
        ).pack(side="right", padx=5)
        ttk.Button(
            right_buttons, text="Edit Prices", command=self.edit_prices, style="TButton"
        ).pack(side="right")

        # Resizable Treeview with Scrollbars
        tree_frame = tk.Frame(self.root, bg=self.light_theme["bg"])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "Order No",
                "Date",
                "Customer",
                "Phone Number",
                "Address",
                "500g Qty",
                "1kg Qty",
                "Total",
                "Status",
            ),
            show="headings",
        )
        self.tree.pack(side="top", fill="both", expand=True)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        # Add a vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        # Add a horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        # Bind the TreeviewSelect event to detect row selection
        self.tree.bind("<<TreeviewSelect>>", self.on_order_select)
        # Load recent orders
        self.load_recent_orders()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        theme = self.dark_theme if self.dark_mode else self.light_theme
        # Update root background
        self.root.configure(bg=theme["bg"])
        # Update all widgets
        self.update_widget_colors(theme)
        # Update dark mode button text
        self.dark_mode_button.config(text="☀️" if self.dark_mode else "🌙")

    def update_widget_colors(self, theme):
        """Update the colors of all widgets based on the selected theme."""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg"])
            elif isinstance(widget, ttk.Label):
                widget.configure(background=theme["bg"], foreground=theme["fg"])
            elif isinstance(widget, ttk.Button):
                widget.configure(style="TButton")
            elif isinstance(widget, ttk.Treeview):
                widget.configure(background=theme["tree_bg"], foreground=theme["tree_fg"])
        # Update Treeview headings
        style = ttk.Style()
        style.configure(
            "Treeview.Heading", background=theme["bg"], foreground=theme["fg"]
        )

    def add_order(self):
        """Add a new order to the system."""
        try:
            name = self.customer_name_var.get()
            phone = self.phone_number_var.get()
            address = self.address_var.get()
            qty_500g = int(self.qty_500g_var.get() or 0)
            qty_1kg = int(self.qty_1kg_var.get() or 0)
            if qty_500g == 0 and qty_1kg == 0:  # Ensure at least one product is selected
                messagebox.showerror(
                    "Error", "Please select at least one product (500g or 1kg)."
                )
                return
            total = float(self.total_var.get())
            order_no = str(uuid.uuid4())[:8]
            date = datetime.now().strftime("%Y-%m-%d")
            status = self.status_var.get()  # Get the order status
            # Ensure phone number is treated as an integer
            phone = int(phone)  # Convert to integer
            # Update the order data in Excel
            df = pd.read_excel(self.excel_file)
            new_order = pd.DataFrame(
                [
                    [
                        order_no,
                        date,
                        name,
                        phone,
                        address,
                        qty_500g,
                        qty_1kg,
                        total,
                        status,
                    ]
                ],
                columns=[
                    "Order No",
                    "Date",
                    "Customer Name",
                    "Phone Number",
                    "Address",
                    "500g Quantity",
                    "1kg Quantity",
                    "Total",
                    "Status",
                ],
            )
            df = pd.concat([df, new_order], ignore_index=True)
            df.to_excel(self.excel_file, index=False)
            self.load_recent_orders()
            messagebox.showinfo("Success", "Order added successfully!")
            self.clear_form()  # Clear form after adding order
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for quantities and phone number."
            )

    def update_order(self):
        """Update an existing order."""
        if not self.selected_order:
            messagebox.showerror("Error", "Please select an order to update.")
            return
        try:
            name = self.customer_name_var.get()
            phone = self.phone_number_var.get()
            address = self.address_var.get()
            qty_500g = int(self.qty_500g_var.get() or 0)
            qty_1kg = int(self.qty_1kg_var.get() or 0)
            if qty_500g == 0 and qty_1kg == 0:
                messagebox.showerror(
                    "Error", "Please select at least one product (500g or 1kg)."
                )
                return
            total = float(self.total_var.get())
            order_no = self.selected_order
            date = datetime.now().strftime("%Y-%m-%d")
            status = self.status_var.get()
            # Ensure phone number is treated as an integer
            phone = int(phone)  # Convert to integer
            df = pd.read_excel(self.excel_file)
            df.loc[
                df["Order No"] == order_no,
                [
                    "Date",
                    "Customer Name",
                    "Phone Number",
                    "Address",
                    "500g Quantity",
                    "1kg Quantity",
                    "Total",
                    "Status",
                ],
            ] = [
                date,
                name,
                phone,
                address,
                qty_500g,
                qty_1kg,
                total,
                status,
            ]
            df.to_excel(self.excel_file, index=False)
            self.load_recent_orders()
            messagebox.showinfo("Success", "Order updated successfully!")
            self.clear_form()  # Clear form after updating order
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for quantities and phone number."
            )

    def delete_order(self):
        """Delete the selected order."""
        if not self.selected_order:
            messagebox.showerror("Error", "Please select an order to delete.")
            return
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this order?")
        if not confirm:
            return
        try:
            # Remove the order from the Excel file
            df = pd.read_excel(self.excel_file)
            df = df[df["Order No"] != self.selected_order]  # Filter out the selected order
            df.to_excel(self.excel_file, index=False)
            # Reload the orders in the Treeview
            self.load_recent_orders()
            messagebox.showinfo("Success", "Order deleted successfully!")
            self.clear_form()  # Clear form after deletion
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting the order: {e}")

    def load_recent_orders(self):
        """Load recent orders into the Treeview."""
        df = pd.read_excel(self.excel_file)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in df.iterrows():
            # Ensure phone number is treated as an integer and formatted correctly
            try:
                phone = int(row["Phone Number"])  # Convert to integer
                phone_str = f"{phone:010d}"  # Format as 10-digit string with leading zeros
            except (ValueError, TypeError):
                phone_str = "Invalid"  # Handle invalid phone numbers gracefully
            self.tree.insert(
                "",
                "end",
                values=(
                    row["Order No"],
                    row["Date"],
                    row["Customer Name"],
                    phone_str,
                    row["Address"],
                    row["500g Quantity"],
                    row["1kg Quantity"],
                    row["Total"],
                    row["Status"],
                ),
            )

    def filter_orders_by_date(self):
        """Filter orders by date range."""
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please enter both start and end dates.")
            return
        df = pd.read_excel(self.excel_file)
        filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in filtered_df.iterrows():
            # Ensure phone number is treated as an integer and formatted correctly
            try:
                phone = int(row["Phone Number"])  # Convert to integer
                phone_str = f"{phone:010d}"  # Format as 10-digit string with leading zeros
            except (ValueError, TypeError):
                phone_str = "Invalid"  # Handle invalid phone numbers gracefully
            self.tree.insert(
                "",
                "end",
                values=(
                    row["Order No"],
                    row["Date"],
                    row["Customer Name"],
                    phone_str,
                    row["Address"],
                    row["500g Quantity"],
                    row["1kg Quantity"],
                    row["Total"],
                    row["Status"],
                ),
            )

    def reset_date_filter(self):
        """Reset the date filter and reload all orders."""
        # Clear the date fields
        self.start_date_var.set("")
        self.end_date_var.set("")
        # Reload all orders into the Treeview
        self.load_recent_orders()
        # Optional: Show a confirmation message
        messagebox.showinfo("Reset", "Date filter has been reset. All orders are now displayed.")

    def clear_form(self):
        """Clear the form fields."""
        self.customer_name_var.set("")
        self.phone_number_var.set("")
        self.address_var.set("")
        self.qty_500g_var.set("0")
        self.qty_1kg_var.set("0")
        self.total_var.set("0.00")
        self.status_var.set("Pending")
        self.selected_order = None  # Reset selected order

    def on_order_select(self, event):
        """Handle order selection from the Treeview."""
        selected_item = self.tree.selection()[0]
        order_data = self.tree.item(selected_item)["values"]
        self.selected_order = order_data[0]
        self.customer_name_var.set(order_data[2])
        self.phone_number_var.set(order_data[3])  # Display phone number as is (string)
        self.address_var.set(order_data[4])
        self.qty_500g_var.set(order_data[5])
        self.qty_1kg_var.set(order_data[6])
        self.total_var.set(order_data[7])
        self.status_var.set(order_data[8])

    def edit_prices(self):
        """Open the edit prices dialog."""
        new_prices = EditPricesDialog(self.root, self.prices, self.save_prices)
        self.root.wait_window(new_prices.top)

    def open_report_dashboard(self):
        """Open the report dashboard."""
        self.dashboard = tk.Toplevel(self.root)
        self.dashboard.title("Report Dashboard")
        self.dashboard.geometry("1000x800")
        self.dashboard.configure(bg="#f0f0f0")
        # Close Button
        close_button = ttk.Button(
            self.dashboard,
            text="Close",
            command=self.dashboard.destroy,
            style="TButton",
        )
        close_button.pack(anchor="ne", padx=10, pady=10)
        # Load data for calculations
        df = pd.read_excel(self.excel_file)
        # Top Section: Metric Boxes (Left-Aligned)
        box_frame = tk.Frame(self.dashboard, bg="#f0f0f0")
        box_frame.pack(side="left", anchor="nw", padx=20, pady=20, fill="y")
        # Total Orders Box
        total_orders = len(df)
        self.create_metric_box(box_frame, "Total Orders", total_orders, "#4CAF50")
        # Total Sales Box
        total_sales = df["Total"].sum()
        self.create_metric_box(box_frame, "Total Sales (Rs)", f"{total_sales:.2f}", "#FF9800")
        # Orders Today Box
        today = datetime.now().strftime("%Y-%m-%d")
        orders_today = len(df[df["Date"] == today])
        self.create_metric_box(box_frame, "Orders Today", orders_today, "#2196F3")
        # Sales Today Box
        sales_today = df[df["Date"] == today]["Total"].sum()
        self.create_metric_box(box_frame, "Sales Today (Rs)", f"{sales_today:.2f}", "#E91E63")
        # Middle Section: Bar Chart and Pie Chart (Side-by-Side)
        chart_frame = tk.Frame(self.dashboard, bg="#f0f0f0")
        chart_frame.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        # Bar Chart (Left Side)
        fig1, ax1 = plt.subplots(figsize=(6, 4))  # Adjust size for better fit
        sales_by_date = df.groupby("Date")["Total"].sum()
        # Create the bar chart
        bars = ax1.bar(sales_by_date.index, sales_by_date.values, color="skyblue")
        ax1.set_title("Sales by Date")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Total Sales (Rs)")
        # Add exact numbers on top of each bar
        ax1.bar_label(bars, fmt='%.2f', label_type='edge', fontsize=8)  # Display values with 2 decimal places
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha="right")
        # Add hover tooltips using mplcursors
        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect(
            "add",
            lambda sel: sel.annotation.set_text(
                f"Date: {sales_by_date.index[sel.target.index]}\nRevenue: {sales_by_date.iloc[sel.target.index]:.2f} Rs"
            ),
        )
        canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
        canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10)
        # Pie Chart (Right Side)
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        revenue_500g = (df["500g Quantity"] * self.prices["500g"]).sum()
        revenue_1kg = (df["1kg Quantity"] * self.prices["1kg"]).sum()
        revenue_breakdown = {"500g": revenue_500g, "1kg": revenue_1kg}
        ax2.pie(revenue_breakdown.values(), labels=revenue_breakdown.keys(), autopct="%1.1f%%", startangle=90)
        ax2.set_title("Revenue Breakdown")
        canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
        canvas2.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10)
        # Bottom Section: Table Below the Bar Chart
        table_frame = tk.Frame(self.dashboard, bg="#f0f0f0")
        table_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=20)
        # Create a Treeview for the table
        self.table = ttk.Treeview(
            table_frame,
            columns=(
                "Date",
                "Total Sales (Rs)",
            ),
            show="headings",
        )
        self.table.pack(side="top", fill="both", expand=True)
        # Configure column headings
        self.table.heading("Date", text="Date")
        self.table.heading("Total Sales (Rs)", text="Total Sales (Rs)")
        self.table.column("Date", width=150)
        self.table.column("Total Sales (Rs)", width=150)
        # Populate the table with data
        for index, row in sales_by_date.items():
            self.table.insert("", "end", values=(index, f"{row:.2f}"))

    def create_metric_box(self, parent, title, value, color):
        """Create a metric box with a title, value, and background color."""
        box = tk.Frame(parent, bg=color, padx=20, pady=20)
        box.pack(side="top", padx=10, pady=10, fill="both", expand=True)
        ttk.Label(box, text=title, font=("Arial", 14, "bold"), background=color, foreground="white").pack()
        ttk.Label(box, text=value, font=("Arial", 18), background=color, foreground="white").pack()

    def generate_receipt(self):
        """Generate a receipt for the selected order and save it as an image."""
        if not self.selected_order:
            messagebox.showerror("Error", "Please select an order to generate a receipt.")
            return

        # Load the selected order data
        df = pd.read_excel(self.excel_file)
        try:
            order_data = df[df["Order No"] == self.selected_order].iloc[0]
        except IndexError:
            messagebox.showerror("Error", "Selected order not found in the database.")
            return

        # Create a blank image for the receipt
        img_width, img_height = 600, 900  # Adjusted height for compact receipt
        receipt_image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(receipt_image)

        # Load the logo
        try:
            logo = Image.open("logo.jpg")
            logo = logo.resize((100, 100))
            receipt_image.paste(logo, (20, 20))  # Paste the logo at the top-left corner
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Set up fonts with increased sizes
        title_font = ImageFont.truetype("arial.ttf", 30)  # Larger font for title
        content_font = ImageFont.truetype("arial.ttf", 20)  # Larger font for content
        small_font = ImageFont.truetype("arial.ttf", 16)  # Slightly larger font for small text

        # Header Section
        draw.text((580, 40), "INVOICE", fill="black", font=title_font, anchor="rm")  # Right-aligned INVOICE
        draw.text((580, 80), f"Date: {order_data['Date']}", fill="black", font=content_font, anchor="rm")  # Right-aligned date below INVOICE

        # Information Section
        y_offset = 140  # Start lower to accommodate larger fonts
        details = [
            f"Order No: {order_data.get('Order No', 'N/A')}",
            f"Customer Name: {order_data.get('Customer Name', 'N/A')}",
            f"Phone Number: {order_data.get('Phone Number', 'N/A')}",
            f"Address: {order_data.get('Address', 'N/A')}",
            "",
            "Items Ordered:",
        ]
        for detail in details:
            draw.text((20, y_offset), detail, fill="black", font=content_font)
            y_offset += 35  # Increased spacing for larger fonts

        # Table for Items
        headers = ["Item", "Qty", "Price", "Total"]
        column_widths = [250, 70, 100, 100]  # Adjust column widths for better alignment
        x_offset = 20
        for i, header in enumerate(headers):
            draw.text((x_offset, y_offset), header, fill="black", font=content_font)
            x_offset += column_widths[i]
        y_offset += 35  # Increased spacing for larger fonts
        x_offset = 20

        # Rows (Only include items with non-zero quantities)
        items = []
        if order_data.get('500g Quantity', 0) > 0:
            items.append(("500g Watalappam", order_data.get('500g Quantity', 0), self.prices["500g"], order_data.get('500g Quantity', 0) * self.prices["500g"]))
        if order_data.get('1kg Quantity', 0) > 0:
            items.append(("1kg Watalappam", order_data.get('1kg Quantity', 0), self.prices["1kg"], order_data.get('1kg Quantity', 0) * self.prices["1kg"]))

        for item in items:
            draw.text((x_offset, y_offset), item[0], fill="black", font=small_font)
            draw.text((x_offset + column_widths[0], y_offset), str(item[1]), fill="black", font=small_font)
            draw.text((x_offset + column_widths[0] + column_widths[1], y_offset), f"{item[2]:.2f}", fill="black", font=small_font)
            draw.text((x_offset + column_widths[0] + column_widths[1] + column_widths[2], y_offset), f"{item[3]:.2f}", fill="black", font=small_font)
            y_offset += 35  # Increased spacing for larger fonts

        # Total Amount
        y_offset += 20
        total_label = "Total Amount:"
        total_value = f"{order_data.get('Total', 0):.2f}"  # Removed "Rs" here
        # Calculate positions for better alignment
        total_label_x = 20
        total_value_x = 400  # Fixed position for the value
        draw.text((total_label_x, y_offset), total_label, fill="black", font=content_font)
        draw.text((total_value_x, y_offset), total_value, fill="black", font=content_font)

        # Thank You Message
        y_offset += 50
        thank_you_message = "Thank you for your order!"
        draw.text((20, y_offset), thank_you_message, fill="black", font=title_font)

        # Contact Information
        y_offset += 60
        try:
            whatsapp_logo = Image.open("whatsapp_logo.png").convert("RGBA")  # Ensure transparency
            whatsapp_logo = whatsapp_logo.resize((40, 40))  # Larger logo size
            receipt_image.paste(whatsapp_logo, (20, y_offset), whatsapp_logo)  # Use mask for transparency
        except Exception as e:
            print(f"Error loading WhatsApp logo: {e}")
        draw.text((70, y_offset + 5), "WhatsApp - 0705081870", fill="black", font=small_font)
        try:
            email_logo = Image.open("email_logo.png").convert("RGBA")  # Ensure transparency
            email_logo = email_logo.resize((40, 40))  # Larger logo size
            receipt_image.paste(email_logo, (20, y_offset + 50), email_logo)  # Use mask for transparency
        except Exception as e:
            print(f"Error loading Email logo: {e}")
        draw.text((70, y_offset + 55), "Email - dessertsmore522@gmail.com", fill="black", font=small_font)

        # Save the receipt image
        receipt_filename = f"{self.receipt_folder}{order_data.get('Order No', 'unknown')}_receipt.png"
        receipt_image.save(receipt_filename)
        messagebox.showinfo("Success", f"Receipt generated successfully! Saved as {receipt_filename}")

    def show_developer_info(self):
        """Show developer information in a new window."""
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("Developer Information")
        self.info_window.geometry("400x300")
        self.info_window.configure(bg="#f5f5f5")

        info_text = """
        💻 Developed by Ravindu Shehara Fernando
        🎓 Undergraduate | University of Colombo
        📚 Bachelor of Information Technology (External)

        📞 Contact: 076-0236389 | 071-4516364
        📩 Email: ravindushehara1234@gmail.com

        For any requirements or inquiries, feel free to reach out!
        """

        info_label = tk.Label(self.info_window, text=info_text, font=("Arial", 12), bg="#f5f5f5", justify="left")
        info_label.pack(pady=20, padx=20)

        close_button = ttk.Button(self.info_window, text="Close", command=self.info_window.destroy, style="TButton")
        close_button.pack(pady=10)


class EditPricesDialog:
    def __init__(self, parent, prices, save_prices_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Prices")
        self.top.geometry("300x200")
        self.prices = prices
        self.save_prices_callback = save_prices_callback
        self.price_500g_var = tk.StringVar(value=str(prices["500g"]))
        self.price_1kg_var = tk.StringVar(value=str(prices["1kg"]))
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.top, text="500g Price:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.price_500g_var).pack(pady=5)
        ttk.Label(self.top, text="1kg Price:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.price_1kg_var).pack(pady=5)
        ttk.Button(self.top, text="Save", command=self.save_prices).pack(pady=10)

    def save_prices(self):
        try:
            price_500g = float(self.price_500g_var.get())
            price_1kg = float(self.price_1kg_var.get())
            self.prices["500g"] = price_500g
            self.prices["1kg"] = price_1kg
            self.save_prices_callback()
            self.top.destroy()
            messagebox.showinfo("Success", "Prices updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid prices.")


if __name__ == "__main__":
    root = tk.Tk()
    app = WatalappamBusinessApp(root)
    root.mainloop()