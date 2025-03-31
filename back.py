# back.py
from flask import render_template, Flask
from Database import Database


class Backend:

    @property
    def app(self) -> Flask:
        return self._app

    @app.setter
    def app(self, app: Flask):
        self._app = app

    def __init__(self):
        self._app = Flask(__name__)
        self._db = Database('test.db')
        self.add_routes()

    def add_routes(self):
        @self._app.route('/')
        def home():
            return render_template('main_screen.html')

        @self._app.route('/register')
        def register():
            data = [
                ('IFID', 10),
                ('GDJK', 20),
                ('JHGF', 10),
                ('JKJD', 30)
            ]
            data = sorted(data, key=lambda x: x[1], reverse=True)
            labels = [row[0] for row in data]
            values = [row[1] for row in data]
            return render_template('lk_screen.html', labels=labels, values=values, percentage=13)

    def run(self, *args, **kwargs):
        self._app.run(*args, **kwargs)
