from flask import Flask, render_template, request, jsonify, abort
import os

app = Flask(__name__)

user_data = {"score": 0, "results": []}

learning_content = {
    "1": {
        "id": "1",
        "title": "Why does turning feel hard?",
        "media_type": "text",
        "points": ["Many beginners lose control when turning", "Turns feel too fast, slippery, and hard to stop"],
        "hint": "Let's fix that by understanding two key techniques.",
        "next": "2"
    },
    "2": {
        "id": "2",
        "title": "What is Skidding?",
        "media_type": "image",
        "media_url": "/static/images/skidding_demo.jpg", 
        "points": ["Board slides sideways", "Less grip on snow", "Easier for beginners", "Less stable at high speed"],
        "next": "3"
    },
    "3": {
        "id": "3",
        "title": "What is Carving?",
        "media_type": "image",
        "media_url": "/static/images/carving_demo.jpg", 
        "points": ["Board edge cuts into snow", "Smooth curved motion", "More control at speed", "Clean and efficient"],
        "next": "4"
    },
    "4": {
        "id": "4",
        "title": "Snow Tracks: The Visual Cue",
        "media_type": "text",
        "points": ["Skidding -> messy, wide tracks", "Carving -> thin, clean lines"],
        "hint": "Looking at tracks is the best way to tell which is which!", 
        "next": "5"
    },
    "5": {
        "id": "5",
        "title": "Scenario: Losing Control!",
        "media_type": "text",
        "points": ["Scenario: You are riding down a steep slope, speed is increasing, and you feel out of control."],
        "question": "What should you use?",
        "options": ["A. Skidding", "B. Carving"],
        "answer": "A. Skidding", 
        "feedback": "Correct! Skidding increases friction to help you slow down.",
        "next": "quiz/1"
    }
}

quiz_content = {
    "1": {"id": "1", "q": "Main difference between carving and skidding?", "options": ["Speed", "Edge vs sliding", "Equipment"], "a": "Edge vs sliding", "next": "2"},
    "2": {"id": "2", "q": "Which technique is easier for beginners?", "options": ["Carving", "Skidding"], "a": "Skidding", "next": "3"},
    "3": {"id": "3", "q": "Which technique gives more control at high speeds?", "options": ["Skidding", "Carving"], "a": "Carving", "next": "4"},
    "4": {"id": "4", "q": "Identify the Carving position:", "media": "/static/images/quiz_carve.jpg", "options": ["A", "B"], "a": "A", "next": "5"},
    "5": {"id": "5", "q": "How can you tell someone is carving by tracks?", "options": ["Wide messy tracks", "Thin clean tracks"], "a": "Thin clean tracks", "next": "results"}
}

@app.route('/')
def home():
    user_data["score"] = 0 
    return render_template('home.html')

@app.route('/learn/<id>')
def learn(id):
    content = learning_content.get(id)
    if content is None:
        abort(404)

    lesson = {
        "title": content.get("title", ""),
        "media": content.get("media_url", ""),
        "text": " ".join(content.get("points", [])),
        "next_lesson": "quiz" if str(content.get("next", "")).startswith("quiz") else content.get("next", "")
    }
    return render_template('learn.html', lesson=lesson)

@app.route('/quiz/<id>')
def quiz(id):
    content = quiz_content.get(id)
    if content is None:
        abort(404)

    question = {
        "quiz_id": content.get("id", id),
        "question": content.get("q", ""),
        "options": content.get("options", []),
        "next_question": "end" if content.get("next") == "results" else content.get("next", "end")
    }
    return render_template('quiz.html', question=question)

@app.route('/record_answer', methods=['POST'])
def record_answer():
    req = request.get_json()
    quiz_id = req.get('quiz_id')
    user_answer = req.get('user_answer')

    if not quiz_id or quiz_id not in quiz_content:
        return jsonify(success=False, error="Invalid quiz_id"), 400

    if user_answer == quiz_content[quiz_id]['a']:
        user_data["score"] += 1
    return jsonify(success=True)

@app.route('/record', methods=['POST'])
def record():
    return record_answer()

@app.route('/results')
def results():
    return render_template('results.html', score=user_data["score"], total=len(quiz_content))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
