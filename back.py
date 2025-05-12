# back.py
from flask import render_template, Flask, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from Database import Database
import plotly.graph_objects as go
import plotly.io as pio
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import time


class Backend:
    def __init__(self):
        self._app = Flask(__name__)
        self._app.secret_key = '4b516967181bf8993a137bbc16f34ed285221f3c9d1a8f470adbe97d60dece32'  # TODO! Убрать это из прода
        self._db = Database('test.db')

        self.login_manager = LoginManager()
        self.login_manager.init_app(self._app)
        self.login_manager.login_view = 'login'

        @self.login_manager.user_loader
        def load_user(user_id):
            return self._db.get_user_by_id(user_id)

        @self.login_manager.unauthorized_handler
        def unauthorized():
            return jsonify({"error": "Unauthorized"}), 401

        self.add_routes()

    @property
    def app(self) -> Flask:
        return self._app

    @app.setter
    def app(self, app: Flask):
        self._app = app

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
        val = sum(answers[39:51])
        result[3] = 'J' if val < 0 else 'P'
        stats[3] = val

        return ''.join(result), stats

    @staticmethod
    def draw_result_statistics(stats):
        print(f"stats: {stats}")
        values = stats
        labels = [['Интроверсия', 'Экстраверсия'], ['Разум', 'Интуиция'], ['Мышление', 'Чувства'],
                  ['Планирование', 'Реагирование']]
        labels_actual = [0, 0, 0, 0]
        for i, el in enumerate(labels):
            labels_actual[i] = el[0] if values[i] < 0 else el[1]

        # Список фиксированных цветов для каждого столбца
        bar_colors = ['#F9897B', '#FEDE95', '#D0E6A6', '#CCADD9']  # Цвета для каждого столбца

        # Создание графика
        fig = go.Figure()

        # Добавление данных с фиксированными цветами для каждого столбца
        fig.add_trace(go.Bar(
            y=labels_actual,
            x=values,
            orientation='h',
            marker=dict(
                color=bar_colors,  # Используем фиксированные цвета
                line=dict(color='black', width=2)  # Черная обводка для столбцов
            ),
            hoverinfo='none'  # Отключаем подсказки при наведении
        ))

        # Добавление аннотаций (подписей слева и справа)
        annotations = []
        for i, label_pair in enumerate(labels):
            left_label, right_label = label_pair
            # Добавляем черную обводку для левой метки
            annotations.append(dict(
                x=-30,  # Позиция для левой метки (можно настроить в зависимости от диапазона)
                y=i,
                text=left_label,
                showarrow=False,
                font=dict(size=12, color="black"),
                align="right",
            ))
            annotations.append(dict(
                x=-30,  # Позиция для левой метки (можно настроить в зависимости от диапазона)
                y=i,
                text=left_label,
                showarrow=False,
                font=dict(size=12, color=bar_colors[i]),
                align="right"
            ))
            annotations.append(dict(
                x=30,  # Позиция для правой метки
                y=i,
                text=right_label,
                showarrow=False,
                font=dict(size=12, color="black"),
                align="left",
            ))
            annotations.append(dict(
                x=30,  # Позиция для правой метки
                y=i,
                text=right_label,
                showarrow=False,
                font=dict(size=12, color=bar_colors[i]),
                align="left"
            ))

        # Настройка графика
        fig.update_layout(
            showlegend=False,
            annotations=annotations,
            dragmode=False,
            template="plotly_white",
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5',
            bargap=0,
            width=600,  # Ширина графика
            height=200,  # Высота графика
            xaxis_range=[-30, 30],  # Диапазон значений на оси X
            yaxis=dict(
                showticklabels=False,  # Отключаем стандартные подписи оси Y
                showline=False,  # Убираем вертикальную линию на оси Y
                autorange="reversed",  # Инвертируем порядок меток по оси Y
            ),
            xaxis=dict(
                showticklabels=False,  # Отключаем горизонтальные метки на оси X
                zeroline=False,  # Убираем вертикальную линию на оси X
                showline=False  # Убираем горизонтальную линию по оси X
            ),
            shapes=[  # Добавляем вертикальную линию в нуле
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': 0,
                    'y0': -0.5,
                    'y1': len(labels) - 0.5,  # Длина графика по оси Y
                    'line': {
                        'color': 'black',
                        'width': 4,
                        'dash': 'solid',
                    }
                }
            ],
            margin=dict(
                l=45,  # Уменьшаем левый отступ
                r=45,  # Уменьшаем правый отступ
                t=0,  # Уменьшаем верхний отступ
                b=0  # Уменьшаем нижний отступ
            ),
        )

        config = {
            'displayModeBar': False  # Отключить верхнюю панель с инструментами
        }

        return pio.to_html(fig, full_html=False, config=config)

    @staticmethod
    def draw_profile_bar_chart(all_user_results):
        print(f"all_user_results: {all_user_results}")
        labels2colors = {
            'ENFJ': '#D58EAC',
            'ENFP': '#E395A3',
            'INFJ': '#FAB6B2',
            'INFP': '#FBD6D9',
            'ISFP': '#F9F2DC',
            'ESFP': '#FEF0B1',
            'ESTP': '#FEDE95',
            'ISTP': '#D0E6A6',
            'ENTJ': '#46C0C1',
            'ENTP': '#89D8E3',
            'INTJ': '#AED2E0',
            'INTP': '#96C3D8',
            'ISFJ': '#56A5BA',
            'ESFJ': '#3592A3',
            'ISTJ': '#B697C2',
            'ESTJ': '#B19CC5'
        }

        labels_actual = []
        values = []
        for i in range(min(3, len(all_user_results))):
            labels_actual.append(all_user_results[i][0])
            values.append(all_user_results[i][1])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=labels_actual,
            x=values,
            orientation='h',
            marker=dict(
                color=[labels2colors[label] for label in labels_actual],
            ),
            hovertemplate='%{y}: %{x}<extra></extra>'
        ))
        fig.update_layout(
            showlegend=False,
            dragmode=False,
            template="plotly_white",
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5',
            bargap=0,
            width=500,  # Ширина графика
            height=300,  # Высота графика
            xaxis_range=[0, max(values)],  # Диапазон значений на оси X
            yaxis=dict(
                showline=False,  # Убираем вертикальную линию на оси Y
                autorange="reversed",  # Инвертируем порядок меток по оси Y
            ),
            xaxis=dict(
                showticklabels=False,  # Отключаем горизонтальные метки на оси X
                zeroline=False,  # Убираем вертикальную линию на оси X
                showline=False  # Убираем горизонтальную линию по оси X
            ),
            shapes=[  # Добавляем вертикальную линию в нуле
                {
                    'type': 'line',
                    'x0': 0,
                    'x1': 0,
                    'y0': -0.5,
                    'y1': len(labels_actual) - 0.5,  # Длина графика по оси Y
                    'line': {
                        'color': 'black',
                        'width': 4,
                        'dash': 'solid',
                    }
                }
            ],
            margin=dict(
                l=45,  # Уменьшаем левый отступ
                r=45,  # Уменьшаем правый отступ
                t=0,  # Уменьшаем верхний отступ
                b=0  # Уменьшаем нижний отступ
            ),
        )

        config = {
            'displayModeBar': False  # Отключить верхнюю панель с инструментами
        }

        return pio.to_html(fig, full_html=False, config=config)

    @staticmethod
    def draw_profile_pie_chart(all_results):
        labels = ['ENFJ', 'ENFP', 'INFJ', 'INFP', 'ISFP', 'ESFP', 'ESTP', 'ISTP', 'ENTJ', 'ENTP', 'INTJ', 'INTP',
                  'ISFJ', 'ESFJ', 'ISTJ', 'ESTJ']
        colors = ['#D58EAC', '#E395A3', '#FAB6B2', '#FBD6D9',
                  '#F9F2DC', '#FEF0B1', '#FEDE95', '#D0E6A6',
                  '#46C0C1', '#89D8E3', '#AED2E0', '#96C3D8',
                  '#56A5BA', '#3592A3', '#B697C2', '#B19CC5']  # Заданные цвета
        values = [all_results.get(label, 0) for label in labels]
        i = 0
        while i < len(values):
            if values[i] == 0:
                del values[i]
                del labels[i]
                del colors[i]
            else:
                i += 1

        # Создаем объект Pie chart, который сохраняет оригинальный порядок
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.7,
            marker=dict(colors=colors),
            textinfo='label',  # Показываем только метки
            hoverinfo='label+percent',  # Показываем метку и процент на всплывающей подсказке
            sort=False,
        ))

        # Настройка внешнего вида
        fig.update_layout(
            width=300,  # Увеличиваем ширину
            height=300,  # Увеличиваем высоту
            margin=dict(t=0, b=0, l=0, r=0),  # Уменьшаем отступы
            showlegend=False,
            template="plotly_white",
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5',
            bargap=0
        )

        fig.update_traces(pull=[0, 0, 0., 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        config = {
            'displayModeBar': False  # Отключить верхнюю панель с инструментами
        }

        return pio.to_html(fig, full_html=False, config=config)

    @staticmethod
    def draw_void(all_results):
        fig = go.Figure()
        fig.update_layout(
            width=300,  # Увеличиваем ширину
            height=300,  # Увеличиваем высоту
            margin=dict(t=0, b=0, l=0, r=0),  # Уменьшаем отступы
            showlegend=False,
            template="plotly_white",
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5',
            bargap=0,
            xaxis=dict(
                showgrid=False,  # Отключить горизонтальную сетку
                zeroline=False,  # Убрать линию нуля
                showline=False,   # Убрать ось X
                showticklabels=False,  # Убрать подписи к меткам оси X
                title=None  # Убрать заголовок оси X
            ),
            yaxis=dict(
                showgrid=False,  # Отключить вертикальную сетку
                zeroline=False,  # Убрать линию нуля
                showline=False,   # Убрать ось Y
                showticklabels=False,  # Убрать подписи к меткам оси Y
                title=None  # Убрать заголовок оси Y
            )
        )
        config = {
            'displayModeBar': False  # Отключить верхнюю панель с инструментами
        }
        return Backend.draw_profile_pie_chart(all_results), pio.to_html(fig, full_html=False, config=config)

    @staticmethod
    def draw_profile_statistics(all_results, all_user_results):
        return Backend.draw_profile_pie_chart(all_results), Backend.draw_profile_bar_chart(all_user_results)

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
                username, password = __handle_login_credentials(data)
                hashed_pw = generate_password_hash(password)
                self._db.add_user(username, hashed_pw)

                user = self._db.get_user_by_username(username)
                login_user(user)

                return jsonify({"OK": "Registration successful"})

        @self._app.route('/login', methods=['POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json()
                username, password = __handle_login_credentials(data)
                user = self._db.get_user_by_username(username)
                if user and check_password_hash(user.password_hash, password):
                    login_user(user)
                    return jsonify({"OK": "Login successful"})
                return jsonify({"error": "Invalid credentials"}), 401
            return jsonify({"error": "Unknown request"}), 400

        def __handle_login_credentials(data):
            # TODO!!! Make it safe!
            print(data)
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            if data.get('username', "") == "" or data.get('password', "") == "":
                return jsonify({"error": "Not enough data"}), 400

            username, password = data['username'], data['password']
            print(f"/login:\nusername: {username}\npassword: {password}\n")
            return username, password

        @self._app.route('/logout')
        @login_required
        def logout():
            logout_user()
            return jsonify({"OK": "Logged out"})

        @self._app.route('/result', methods=['POST'])
        def get_result():
            print('ENTERED get_result')
            data = request.get_json()
            answers = data.get('answers', None)
            if answers is None:
                return jsonify({"error": "No answers in JSON"}), 400
            result, stats = self._calculate_result(answers)
            self._db.write_test_answer(result, {'answers': answers, 'user_id': current_user.id, 'test_id': 1, 'datetime': time.time()})
            print('READY TO REDIRECT')
            print(f"result: {result}, stats: {stats}")
            return redirect(url_for('show_result', result=result, stats=','.join(map(str, stats))))

        @self._app.route('/show_result', methods=['GET'])
        def show_result():
            print('ENTERED show_result')
            result = request.args.get('result')
            stats = request.args.get('stats')
            stats = list(map(int, stats.split(',')))
            print(f"result: {result}, stats: {stats}")
            print('READY TO RENDER')
            graph = self.draw_result_statistics(stats)
            return render_template('view_result.html', result=result, graph_html=graph)

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

        @self._app.route('/profile', methods=['GET'])
        def show_profile():
            uid = current_user.id

            all_results = {item[0]: item[1] for item in self._db.get_statistics()}
            all_user_results = sorted(self._db.get_user_statistics(uid), key=lambda x: x[1], reverse=True)
            user_result = self._db.get_latest_result(uid)

            if len(all_user_results) > 0 and len(all_user_results[0]) > 0:
                percentage = int(round(all_results[all_user_results[0][0]] / sum(all_results.values()) * 100))
            else:
                percentage = 0
            if user_result is None:
                user_result = 'ENFJ'
                pie_chart, bar_chart = self.draw_void(all_results)
            else:
                pie_chart, bar_chart = self.draw_profile_statistics(all_results, all_user_results)
            return render_template(
                'profile_page.html',
                percentage=percentage,
                user_result=user_result,
                pie_chart=pie_chart,
                bar_chart=bar_chart
            )
        @self._app.route('/info')
        def info():
            return render_template('info.html')

        @self._app.route('/description')
        def description():
            return render_template('description.html')


    def run(self, *args, **kwargs):
        self._app.run(*args, **kwargs)
