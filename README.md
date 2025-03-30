# Book Catalog Management System

A Python-based GUI application for managing a book catalog using Tkinter and MySQL.

## Features

- Add new books to the catalog
- View all books in a table format
- Update existing book information
- Input validation and error handling
- MySQL database integration

## Prerequisites

- Python 3.x
- MySQL Server
- MySQL Connector for Python

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure MySQL Server is running on your system.

3. Update the database connection details in `book_catalog.py` if needed:
```python
self.conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="book_catalog"
)
```

## Usage

1. Run the application:
```bash
python book_catalog.py
```

2. The main menu will appear with three options:
   - Add New Book: Opens a form to add a new book
   - View Books: Displays all books in a table format
   - Update Book: Opens a form to update existing book information

3. When adding or updating a book:
   - Fill in all required fields
   - Use the format YYYY-MM-DD for the publication date
   - Click the respective button to save changes

## Database Structure

The application uses a MySQL database with the following structure:

```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    publication_date DATE NOT NULL
);
```

## Error Handling

The application includes validation for:
- Required fields
- Date format (YYYY-MM-DD)
- Database connection errors
- Invalid book IDs when updating 