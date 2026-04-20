from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

user_stats = {
    "score": 0,
    "answers": []
}

lessons = {
    "1": {
        "lesson_id": "1",
        "title": "Understanding Skidding",
        "media": "https://example.com/skidding_video.mp4", 
        "text": "Skidding is when your board slides sideways. It's great for slowing down but less stable at high speeds.",
        "next_lesson": "2"
    },
    "2": {
        "lesson_id": "2",
        "title": "The Art of Carving",
        "media": "https://example.com/carving_video.mp4",
        "text": "Carving involves cutting the edge of the board into the snow. It provides maximum control and efficiency.",
        "next_lesson": "quiz" 
    }
}

quiz_data = {
    "1": {
        "quiz_id": "1",
        "question": "Which technique leaves a thin, clean line in the snow?",
        "options": ["Skidding", "Carving"],
        "answer": "Carving",
        "next_question": "2"
    },
    "2": {
        "quiz_id": "2",
        "question": "What is the primary focus of carving?",
        "options": ["Sliding sideways", "Edge control"],
        "answer": "Edge control",
        "next_question": "end"
    }
}


@app.route('/')
def home():
    global user_stats
    user_stats = {"score": 0, "answers": []} 
    return render_template('home.html')

@app.route('/learn/<lesson_id>')
def learn(lesson_id):
    lesson = lessons.get(lesson_id)
    return render_template('learn.html', lesson=lesson)

@app.route('/quiz/<quiz_id>')
def quiz(quiz_id):
    question = quiz_data.get(quiz_id)
    return render_template('quiz.html', question=question)

@app.route('/record_answer', methods=['POST'])
def record_answer():
    data = request.get_json()
    correct_answer = quiz_data[data['quiz_id']]['answer']
    is_correct = (data['user_answer'] == correct_answer)
    
    if is_correct:
        user_stats["score"] += 1
    user_stats["answers"].append(is_correct)
    
    return jsonify(success=True)

@app.route('/results')
def results():
    return render_template('results.html', score=user_stats["score"], total=len(quiz_data))

if __name__ == '__main__':
    app.run(debug=True)
