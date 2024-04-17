from website import create_app
from flask_migrate import Migrate
from website import db


app = create_app()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)