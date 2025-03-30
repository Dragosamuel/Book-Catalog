import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import re

class BookCatalog:
    def __init__(self):
        """
        Initialize the Book Catalog application
        Sets up the main window, styles, database connection, and UI components
        """
        print("Initializing BookCatalog...")
        self.root = tk.Tk()
        self.root.title("Book Catalog Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TButton', padding=10, font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', padding=5)
        self.style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Helvetica', 12))
        
        # Configure colors
        self.colors = {
            'primary': '#2196F3',  # Blue
            'secondary': '#FFC107',  # Amber
            'success': '#4CAF50',  # Green
            'error': '#F44336',  # Red
            'background': '#f0f0f0',
            'text': '#212121'
        }
        
        # Database connection
        try:
            print("Attempting to connect to MySQL...")
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="24/bse/bu/0010",
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.conn.cursor()
            print("Successfully connected to MySQL!")
            
            # Create database if it doesn't exist
            print("Creating database if it doesn't exist...")
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS book_catalog")
            self.cursor.execute("USE book_catalog")
            print("Database setup complete!")
            
        except mysql.connector.Error as err:
            print(f"MySQL Connection Error: {err}")
            messagebox.showerror("Database Connection Error", 
                f"Could not connect to MySQL server. Please make sure:\n"
                f"1. MySQL Server is installed\n"
                f"2. MySQL service is running\n"
                f"3. The password is correct\n\n"
                f"Error: {err}")
            self.root.destroy()
            return
        
        # Create database and table if they don't exist
        print("Setting up database tables...")
        self.setup_database()
        
        # Create main menu
        print("Creating main menu...")
        self.create_main_menu()
        print("Initialization complete!")
        
    def setup_database(self):
        """
        Create the books table if it doesn't exist
        Defines the structure for storing book information
        """
        # Create books table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                publication_date DATE NOT NULL
            )
        """)
        self.conn.commit()
        
    def create_main_menu(self):
        """
        Create the main menu interface with buttons and descriptions
        """
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with subtitle
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 40))
        
        header = ttk.Label(header_frame, text="Book Catalog", 
                          style='Header.TLabel', padding=(0, 0, 0, 10))
        header.pack()
        
        subtitle = ttk.Label(header_frame, text="Manage your book collection with ease", 
                           style='Subheader.TLabel')
        subtitle.pack()
        
        # Create button frame with grid layout
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Create main menu buttons with icons and descriptions
        buttons = [
            ("Add New Book", self.show_add_form, "Add a new book to your catalog"),
            ("View Books", self.show_view_form, "Browse your book collection"),
            ("Update Book", self.show_update_form, "Modify existing book information")
        ]
        
        for i, (text, command, description) in enumerate(buttons):
            # Create a frame for each button and its description
            btn_container = ttk.Frame(button_frame)
            btn_container.pack(pady=10, padx=20, fill=tk.X)
            
            # Button
            btn = ttk.Button(btn_container, text=text, command=command, width=20)
            btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Description label
            desc = ttk.Label(btn_container, text=description, style='Subheader.TLabel')
            desc.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
    def show_add_form(self):
        """
        Create and show the form for adding new books
        """
        # Create new window for adding books
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Book")
        add_window.geometry("500x400")
        add_window.transient(self.root)
        add_window.grab_set()
        add_window.configure(bg=self.colors['background'])
        
        # Create main frame
        main_frame = ttk.Frame(add_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with subtitle
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 20))
        
        header = ttk.Label(header_frame, text="Add New Book", 
                          style='Header.TLabel', padding=(0, 0, 0, 10))
        header.pack()
        
        subtitle = ttk.Label(header_frame, text="Enter the book details below", 
                           style='Subheader.TLabel')
        subtitle.pack()
        
        # Create form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields with better layout
        fields = [
            ("Title:", "title", "Enter the book title"),
            ("Author:", "author", "Enter the author's name"),
            ("Genre:", "genre", "Enter the book genre"),
            ("Publication Date:", "date", "YYYY-MM-DD format")
        ]
        
        entries = {}
        for label_text, field_name, placeholder in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=10)
            
            label = ttk.Label(frame, text=label_text, width=25)
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e, entry=entry, placeholder=placeholder: 
                      self.on_entry_click(e, entry, placeholder))
            entry.bind('<FocusOut>', lambda e, entry=entry, placeholder=placeholder: 
                      self.on_focus_out(e, entry, placeholder))
            entries[field_name] = entry
        
        def add_book():
            """
            Handle adding a new book to the database
            Includes validation and error handling
            """
            # Validate inputs
            if not all(entry.get() and entry.get() not in ["Enter the book title", 
                                                          "Enter the author's name",
                                                          "Enter the book genre",
                                                          "YYYY-MM-DD format"] 
                      for entry in entries.values()):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            # Validate date format
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, entries['date'].get()):
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
                
            try:
                # Insert book into database
                self.cursor.execute("""
                    INSERT INTO books (title, author, genre, publication_date)
                    VALUES (%s, %s, %s, %s)
                """, (entries['title'].get(), entries['author'].get(), 
                      entries['genre'].get(), entries['date'].get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Book added successfully!")
                add_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Add Book", command=add_book, width=20).pack()
        
        # Center the window
        add_window.update_idletasks()
        width = add_window.winfo_width()
        height = add_window.winfo_height()
        x = (add_window.winfo_screenwidth() // 2) - (width // 2)
        y = (add_window.winfo_screenheight() // 2) - (height // 2)
        add_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_entry_click(self, event, entry, placeholder):
        """
        Handle focus in event for entry fields
        Removes placeholder text when field is focused
        """
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground='black')
            
    def on_focus_out(self, event, entry, placeholder):
        """
        Handle focus out event for entry fields
        Restores placeholder text if field is empty
        """
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(foreground='grey')
            
    def show_view_form(self):
        """
        Create and show the form for viewing all books
        Displays books in a table format with scrollbar
        """
        # Create new window for viewing books
        view_window = tk.Toplevel(self.root)
        view_window.title("View Books")
        view_window.geometry("800x600")
        view_window.transient(self.root)
        view_window.grab_set()
        view_window.configure(bg=self.colors['background'])
        
        # Create main frame
        main_frame = ttk.Frame(view_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with subtitle
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 20))
        
        header = ttk.Label(header_frame, text="Book Catalog", 
                          style='Header.TLabel', padding=(0, 0, 0, 10))
        header.pack()
        
        subtitle = ttk.Label(header_frame, text="Your complete book collection", 
                           style='Subheader.TLabel')
        subtitle.pack()
        
        # Create treeview frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for displaying books
        columns = ("ID", "Title", "Author", "Genre", "Publication Date")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Set column headings and widths
        column_widths = {
            "ID": 50,
            "Title": 300,
            "Author": 200,
            "Genre": 150,
            "Publication Date": 100
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths[col])
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fetch and display books
        try:
            self.cursor.execute("SELECT * FROM books")
            books = self.cursor.fetchall()
            
            for book in books:
                tree.insert("", tk.END, values=book)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
            
        # Center the window
        view_window.update_idletasks()
        width = view_window.winfo_width()
        height = view_window.winfo_height()
        x = (view_window.winfo_screenwidth() // 2) - (width // 2)
        y = (view_window.winfo_screenheight() // 2) - (height // 2)
        view_window.geometry(f'{width}x{height}+{x}+{y}')
            
    def show_update_form(self):
        """
        Create and show the form for updating existing books
        Allows loading and modifying book information
        """
        # Create new window for updating books
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Book")
        update_window.geometry("500x500")
        update_window.transient(self.root)
        update_window.grab_set()
        update_window.configure(bg=self.colors['background'])
        
        # Create main frame
        main_frame = ttk.Frame(update_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with subtitle
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 20))
        
        header = ttk.Label(header_frame, text="Update Book", 
                          style='Header.TLabel', padding=(0, 0, 0, 10))
        header.pack()
        
        subtitle = ttk.Label(header_frame, text="Modify existing book information", 
                           style='Subheader.TLabel')
        subtitle.pack()
        
        # Create form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create form fields with better layout
        fields = [
            ("Book ID:", "id", "Enter the book ID"),
            ("Title:", "title", "Enter the book title"),
            ("Author:", "author", "Enter the author's name"),
            ("Genre:", "genre", "Enter the book genre"),
            ("Publication Date:", "date", "YYYY-MM-DD format")
        ]
        
        entries = {}
        for label_text, field_name, placeholder in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=10)
            
            label = ttk.Label(frame, text=label_text, width=25)
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e, entry=entry, placeholder=placeholder: 
                      self.on_entry_click(e, entry, placeholder))
            entry.bind('<FocusOut>', lambda e, entry=entry, placeholder=placeholder: 
                      self.on_focus_out(e, entry, placeholder))
            entries[field_name] = entry
        
        def load_book():
            """
            Load book information into the form
            Fetches book details from database based on ID
            """
            try:
                book_id = entries['id'].get()
                if not book_id or book_id == "Enter the book ID":
                    messagebox.showerror("Error", "Please enter a book ID!")
                    return
                    
                self.cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
                book = self.cursor.fetchone()
                
                if book:
                    entries['title'].delete(0, tk.END)
                    entries['title'].insert(0, book[1])
                    entries['author'].delete(0, tk.END)
                    entries['author'].insert(0, book[2])
                    entries['genre'].delete(0, tk.END)
                    entries['genre'].insert(0, book[3])
                    entries['date'].delete(0, tk.END)
                    entries['date'].insert(0, book[4].strftime("%Y-%m-%d"))
                else:
                    messagebox.showerror("Error", "Book not found!")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")
                
        def update_book():
            """
            Handle updating book information in the database
            Includes validation and error handling
            """
            # Validate inputs
            if not all(entry.get() and entry.get() not in ["Enter the book ID",
                                                          "Enter the book title", 
                                                          "Enter the author's name",
                                                          "Enter the book genre",
                                                          "YYYY-MM-DD format"] 
                      for entry in entries.values()):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            # Validate date format
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, entries['date'].get()):
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
                
            try:
                # Update book in database
                self.cursor.execute("""
                    UPDATE books 
                    SET title = %s, author = %s, genre = %s, publication_date = %s
                    WHERE id = %s
                """, (entries['title'].get(), entries['author'].get(), 
                      entries['genre'].get(), entries['date'].get(), 
                      entries['id'].get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Book updated successfully!")
                update_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Load Book", command=load_book, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Update Book", command=update_book, width=20).pack(pady=5)
        
        # Center the window
        update_window.update_idletasks()
        width = update_window.winfo_width()
        height = update_window.winfo_height()
        x = (update_window.winfo_screenwidth() // 2) - (width // 2)
        y = (update_window.winfo_screenheight() // 2) - (height // 2)
        update_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def run(self):
        """
        Start the application main loop
        """
        self.root.mainloop()

if __name__ == "__main__":
    app = BookCatalog()
    app.run() 