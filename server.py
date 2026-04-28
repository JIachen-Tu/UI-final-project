from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
import os
import time

app = Flask(__name__)

user_data = {"score": 0, "results": {}, "learn_enter_time": {}, "learn_stay_time": {}}

learning_content = {
    "1": {
        "id": "1",
        "title": "Why does turning feel hard?",
        "media_type": "video",
        "media_url": "/static/videos/snowboarding.mp4",
        "points": [
            "Many beginners lose control when turning",
            "Turns feel too fast, slippery, and hard to stop"
        ],
        "hint": "Let's fix that by understanding two key techniques.",
        "next": "2"
    },
    "2": {
        "id": "2",
        "title": "What is Skidding?",
        "media_type": "video",
        "media_url": "/static/videos/snowboarding.mp4",
        "points": [
            "Board slides sideways",
            "Less grip on snow",
            "Easier for beginners",
            "Less stable at high speed"
        ],
        "next": "3"
    },
    "3": {
        "id": "3",
        "title": "What is Carving?",
        "media_type": "video",
        "media_url": "/static/videos/snowboarding.mp4",
        "points": [
            "Board edge cuts into snow",
            "Smooth curved motion",
            "More control at speed",
            "Clean and efficient"
        ],
        "next": "4"
    },
    "4": {
        "id": "4",
        "title": "Snow Tracks: The Visual Cue",
        "media_type": "video",
        "media_url": "/static/videos/snowboarding.mp4",
        "points": [
            "Skidding -> messy, wide tracks",
            "Carving -> thin, clean lines"
        ],
        "hint": "Looking at tracks is the best way to tell which is which!",
        "next": "5"
    },
    "5": {
        "id": "5",
        "title": "Scenario: Losing Control!",
        "media_type": "video",
        "media_url": "/static/videos/snowboarding.mp4",
        "points": [
            "Scenario: You are riding down a steep slope, speed is increasing, and you feel out of control."
        ],
        "question": "What should you use?",
        "options": ["A. Skidding", "B. Carving"],
        "answer": "A. Skidding",
        "feedback": "Correct! Skidding increases friction to help you slow down.",
        "next": "quiz/1"
    }
}

quiz_content = {
    "1": {
        "id": "1", 
        "q": "Main difference between carving and skidding?", 
        "options": ["Speed", "Edge vs sliding", "Equipment"], 
        "a": "Edge vs sliding", 
        "next": "2"
    },
    "2": {
        "id": "2", 
        "q": "Which technique is easier for beginners?", 
        "options": ["Carving", "Skidding"], 
        "a": "Skidding", 
        "next": "3"
    },
    "3": {
        "id": "3", 
        "q": "Which technique gives more control at high speeds?",  
        "options": ["Skidding", "Carving"], 
        "a": "Carving", 
        "next": "4"
    },
    "4": {
        "id": "4", 
        "q": "Identify the Carving position:", 
        "options": ["A", "B"], 
        "a": "A", 
        "next": "5"
    },
    "5": {
        "id": "5", 
        "q": "How can you tell someone is carving by tracks?", 
        "options": ["Wide messy tracks", "Thin clean tracks"], 
        "a": "Thin clean tracks", 
        "next": "results"
    }
}



@app.route('/')
def home():
    user_data["score"] = 0
    user_data["results"] = {}
    user_data["learn_enter_time"] = {}
    user_data["learn_stay_time"] = {}
    return render_template('home.html')

@app.route('/learn/<id>')
def learn(id):
    content = learning_content.get(id)
    if content is None:
        abort(404)
    
    lesson_id = int(id)
    user_data["learn_enter_time"][lesson_id] = time.time()
    if lesson_id != 1:
        user_data["learn_stay_time"][lesson_id - 1] = user_data["learn_enter_time"][lesson_id] - user_data["learn_enter_time"][lesson_id - 1]

    lesson = {
        "title": content.get("title", ""),
        "lesson_id": lesson_id,
        "media": content.get("media_url", ""),
        "text": " ".join(content.get("points", [])),
        "next_lesson": "quiz" if str(content.get("next", "")).startswith("quiz") else content.get("next", "")
    }
    
    return render_template('learn.html', lesson=lesson)

@app.route('/learn/last_page', methods=["POST"])
def learn_last_page():
    req = request.get_json()
    
    lesson_id = req.get("id")
    
    if lesson_id is None:
        return jsonify(success=False, error="Missing lesson id"), 400

    lesson_id = int(lesson_id)
    user_data["learn_stay_time"][lesson_id] = time.time() - user_data["learn_enter_time"][lesson_id]
    
    return jsonify(success=True)


@app.route('/quiz/<id>')
def quiz(id):
    content = quiz_content.get(id)
    if content is None:
        abort(404)
    
    id = content.get("id", id)
    
    if id == 1 and user_data["score"] != 0:
        user_data["score"] = 0
        user_data["results"] = {}

    question = {
        "quiz_id": content.get("id", id),
        "question": content.get("q", ""),
        "options": content.get("options", []),
        "media": content.get("media", ""),
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
    user_data["results"][quiz_id] = user_answer
    
    return jsonify(success=True)

@app.route('/record', methods=['POST'])
def record():
    return record_answer()

@app.route('/retake')
def retake():
    user_data["score"] = 0
    user_data["results"] = {}
    return redirect(url_for('quiz', id='1'))

@app.route('/results')
def results():
    return render_template('results.html', score=user_data["score"], total=len(quiz_content))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
