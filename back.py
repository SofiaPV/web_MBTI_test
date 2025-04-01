# back.py
from flask import render_template, Flask, request, jsonify
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

    def _calculate_result(self, answers):
        """
        calculates MBTI type
        :param answers: user answers
        :return: type (str) as 4 letters
        """
        return 'INFJ'

    def add_routes(self):
        @self._app.route('/')
        def home():
            return render_template('main_screen.html')

        @self._app.route('/register', methods=['POST', 'GET'])
        def register():
            if request.method == 'GET':
                return render_template('register_page.html')
            if request.method == 'POST':
                data = request.get_json()
                print(data)
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
                if data.get('username', "") == "" or data.get('password', "") == "":
                    return jsonify({"error": "Not enough data"}), 400

                username, password = data['username'], data['password']
                print(f"/register:\nusername: {username}\npassword: {password}\n")
                # your code hear :)

                return jsonify({"OK": "ok!!!"})

        @self._app.route('/login', methods=['POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json()
                print(data)
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
                if data.get('username', "") == "" or data.get('password', "") == "":
                    return jsonify({"error": "Not enough data"}), 400

                username, password = data['username'], data['password']
                print(f"/login:\nusername: {username}\npassword: {password}\n")
                # your code hear :)

                return jsonify({"OK": "ok!!!"})

            return jsonify({"error": "Unknown request"}), 400

        @self._app.route('/save', methods=['POST'])
        def save():
            if request.method == 'POST':
                data = request.get_json()
                answers = data.get('answers', None)
                if answers is None:
                    jsonify({"error": "No answers in JSON"}), 400
                result = self._calculate_result(answers)
                # self._db.write_test_answer(result, data)
                # тут надо уточнить всякое

                return jsonify({"OK": "ok!!!"})
            return jsonify({"error": "Unknown request"}), 400

    def run(self, *args, **kwargs):
        self._app.run(*args, **kwargs)
