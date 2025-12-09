from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Простая "база данных" в JSON файле
DB_FILE = 'grades.json'

def load_grades():
    """Загружает оценки из файла"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"students": []}

def save_grades(data):
    """Сохраняет оценки в файл"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/grades')
def show_grades():
    """Страница с оценками"""
    data = load_grades()
    return render_template('grades.html', students=data['students'])

@app.route('/api/grades', methods=['GET'])
def get_grades():
    """API для получения оценок (JSON)"""
    data = load_grades()
    return jsonify(data)

@app.route('/api/grades', methods=['POST'])
def add_grade():
    """API для добавления новой оценки"""
    data = load_grades()
    
    new_grade = {
        'id': len(data['students']) + 1,
        'student_name': request.json.get('student_name'),
        'subject': request.json.get('subject'),
        'grade': request.json.get('grade'),
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    data['students'].append(new_grade)
    save_grades(data)
    
    return jsonify({"message": "Оценка добавлена", "grade": new_grade}), 201

@app.route('/api/stats')
def get_stats():
    """API для статистики (НОВАЯ ФУНКЦИОНАЛЬНОСТЬ)"""
    data = load_grades()
    
    if not data['students']:
        return jsonify({"message": "Нет данных"})
    
    # Считаем средний балл
    grades = [s['grade'] for s in data['students'] if isinstance(s['grade'], (int, float))]
    
    stats = {
        'total_students': len(set(s['student_name'] for s in data['students'])),
        'total_grades': len(data['students']),
        'average_grade': round(sum(grades) / len(grades), 2) if grades else 0,
        'subjects': list(set(s['subject'] for s in data['students']))
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    # Создаем файл с тестовыми данными, если его нет
    if not os.path.exists(DB_FILE):
        test_data = {
            "students": [
                {"id": 1, "student_name": "Иванов Иван", "subject": "Математика", "grade": 5, "date": "2024-01-15"},
                {"id": 2, "student_name": "Петрова Анна", "subject": "Программирование", "grade": 4, "date": "2024-01-16"},
                {"id": 3, "student_name": "Сидоров Алексей", "subject": "Базы данных", "grade": 3, "date": "2024-01-17"}
            ]
        }
        save_grades(test_data)
    
    app.run(debug=True, port=5000)