# back.py
from flask import render_template, Flask, request, jsonify, redirect, url_for
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

    @staticmethod
    def _calculate_result(answers):
        """
        calculates MBTI type
        :param  answers: user answers (List)
                Introversion: -1 Extraversion: +1
                Sensing: -1 Intuition(N): +1
                Thinking: -1 Feeling: +1
                Judging: -1 Perceiving: +1
        :return: type (str) as 4 letters
        """
        result = [0, 0, 0, 0]
        stats = [0, 0, 0, 0]

        val = sum(answers[:11])
        result[0] = 'I' if val < 0 else 'E'
        stats[0] = val
        val = sum(answers[11:25])
        result[1] = 'S' if val < 0 else 'N'
        stats[1] = val
        val = sum(answers[25:39])
        result[2] = 'T' if val < 0 else 'F'
        stats[2] = val
        val = sum(answers[39:])
        result[3] = 'J' if val < 0 else 'P'
        stats[3] = val

        return ''.join(result), stats

    def add_routes(self):
        @self._app.route('/')
        def home():
            return render_template('main_screen.html')
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

        @self._app.route('/result', methods=['POST'])
        def get_result():
            print('ENETERED get_result')
            data = request.get_json()
            answers = data.get('answers', None)
            if answers is None:
                return jsonify({"error": "No answers in JSON"}), 400
            result, stats = self._calculate_result(answers)
            print('READY TO REDIRECT')
            print(f"result: {result}, stats: {stats}")
            return redirect(url_for('show_result', result=result, stats=','.join(map(str, stats))))

        @self._app.route('/show_result', methods=['GET'])
        def show_result():
            print('ENETERED show_result')
            result = request.args.get('result')
            stats = request.args.get('stats')
            stats = list(map(int, stats.split(',')))
            print(f"result: {result}, stats: {stats}")
            print('READY TO RENDER')
            return render_template('view_result.html', result=result)


        @self._app.route('/save', methods=['POST'])
        def save():
            if request.method == 'POST':
                data = request.get_json()
                answers = data.get('answers', None)
                if answers is None:
                    jsonify({"error": "No answers in JSON"}), 400
                result = self._calculate_result(answers)[0]
                self._db.write_test_answer(result, data)

                return jsonify({"OK": "ok!!!"})
            return jsonify({"error": "Unknown request"}), 400

        @self._app.route('/test', methods=['GET'])
        def show_test():
            return render_template('test_page.html')


    def run(self, *args, **kwargs):
        self._app.run(*args, **kwargs)
