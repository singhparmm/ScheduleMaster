import pytest
from flask_testing import TestCase
from ScheduleMaster import create_app, db
from ScheduleMaster.website.models import Note
from datetime import datetime  # to take date input

class TestNoteAdding(TestCase):
    def create_app(self):
        # Create a Flask application configured for testing
        return create_app('testing')

    def setUp(self):
        # Setup the database for testing; this runs before each test method
        db.create_all()

    def tearDown(self):
        # Teardown the database; this runs after each test method
        db.session.remove()
        db.drop_all()

    def test_add_note_success(self):
        # Test adding a valid note
        date_time_str = '2023-10-01 14:00'
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')

        response = self.client.post('/add_note', data={
            'title': 'Meeting',
            'data': 'Discuss project',  # Corrected from 'content' to 'data'
            'date': date_time_obj,  # Ensuring date is a datetime object
            'hour': 14  # Ensuring hour is an integer
        }, follow_redirects=True)
        assert response.status_code == 200
        assert Note.query.count() == 1
        note = Note.query.first()
        assert note.title == 'Meeting'
        assert note.data == 'Discuss project'  # Changed to 'data'
        assert note.date.date() == date_time_obj.date()  # Check if the date matches
        assert note.hour == 14  # Check if the hour matches

    def test_add_note_failure(self):
        # Test adding a note with invalid data
        response = self.client.post('/add_note', data={
            'title': '',  # Missing title
            'data': 'No title provided',  # Corrected from 'content' to 'data'
            'date': '2023-10-01',  # Assuming date validation is handled elsewhere
            'hour': '14'  # Assuming hour validation is handled elsewhere
        }, follow_redirects=True)
        assert response.status_code == 200 or response.status_code == 400  # Depending on your form validation logic
        assert Note.query.count() == 0  # No new note should be added if the title is missing

# To run the tests
if __name__ == "__main__":
    pytest.main()
