# Remote Education API

This is a Django REST Framework API for a remote education application. It provides functionality for students, teachers, and parents.

## Features

- **User Roles:** Students, Teachers, and Parents.
- **Groups:** Teachers can create groups and invite students using a unique code.
- **Tasks:** Teachers can create tasks with a title and expiration date.
- **Solutions:** Students can submit solutions to tasks before they expire.
- **Grading:** Teachers can grade solutions.
- **Parent View:** Parents can view their child's task list with statuses (graded, not done, expired).

## Technologies Used

- Django
- Django REST Framework
- Djoser (for authentication)
- MSSQL
- Python

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the database:**
   - Open `mpitfinal2026backend/settings.py`.
   - Update the `DATABASES` setting with your MSSQL server details.

6. **Run the migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`.
