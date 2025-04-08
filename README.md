# Cricket Club Management System

A comprehensive web application for managing cricket clubs, teams, players, and matches. Built with Flask and PostgreSQL.

## Features

- Player Management
  - Add, edit, and remove players
  - Track player roles and contact information
  - Manage player memberships

- Team Management
  - Create and manage teams
  - Assign coaches and captains
  - Track team composition

- Match Management
  - Schedule matches between teams
  - Record match results
  - Track match locations and grounds

- Scorecard Management
  - Record player performance
  - Track runs and wickets
  - Generate match statistics

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cricket-club
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python init_db.py
```

5. Configure the application:
- Update the database credentials in `config.py` if needed
- Set up environment variables if required

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Database Schema

The application uses the following database schema:

- PLAYER: Stores player information
- TEAM: Manages team details
- MATCH: Tracks match schedules and results
- ADMIN: Handles administrative users
- MEMBERSHIP: Manages player memberships
- SCORECARD: Records match performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 