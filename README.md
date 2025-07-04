# KanMind Backend

A Django REST API backend for a Kanban-style project management application.

## Features

- User authentication with token-based auth
- Board management with member permissions
- Task management with status tracking
- Comment system for tasks
- Email availability checking
- Task assignment and review system

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kanmind_backend
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Server

1. Start the development server:
```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/registration/` - Register new user
- `POST /api/auth/login/` - User login
- `GET /api/auth/email-check/` - Check email availability

### Boards
- `GET /api/boards/` - List all boards
- `POST /api/boards/` - Create new board
- `GET /api/boards/<id>/` - Get board details
- `PUT /api/boards/<id>/` - Update board
- `DELETE /api/boards/<id>/` - Delete board

### Tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/<id>/` - Get task details
- `PUT /api/tasks/<id>/` - Update task
- `DELETE /api/tasks/<id>/` - Delete task
- `GET /api/tasks/assigned-to-me/` - Get tasks assigned to current user
- `GET /api/tasks/reviewing/` - Get tasks to review

### Comments
- `GET /api/tasks/<id>/comments/` - List task comments
- `POST /api/tasks/<id>/comments/` - Add comment
- `PUT /api/tasks/<id>/comments/<id>/` - Update comment
- `DELETE /api/tasks/<id>/comments/<id>/` - Delete comment

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
