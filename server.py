from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, session
import os
import time

app = Flask(__name__)

app.secret_key = "snowboarding_secret_key" 


user_data = {
    "score": 0,                # last finalized quiz score (shown on /results)
    "results": {},             # last finalized answer map
    "score_attempt": 0,        # in-progress accumulator
    "results_attempt": {},     # in-progress answer map
    "learn_enter_time": {},
    "learn_stay_time": {},
}

learning_content = {
    "1": {
        "id": "1",
        "title": "Why does turning feel hard?",
        "media_type": "video",
        "media_url": "/static/videos/learn_1.mp4",
        "points": [
            "Many beginners lose control when turning",
            "Turns feel too fast, slippery, and hard to stop"
        ],
        "hint": "Let's fix that by understanding two key techniques.",
        "next_preview": {
            "title": "Step 2: What is Skidding?",
            "description": "Learn how skidded turns help beginners slow down and stay in control.",
            "icon": "step-icon-skidding"
        },
        "prev": "",
        "next": "/learn/2"
    },
    "2": {
        "id": "2",
        "title": "What is Skidding?",
        "media_type": "video",
        "media_url": "/static/videos/learn_2.mp4",
        "note": "How to make basic skidded turns.",
        "points": [
            "Board slides sideways",
            "Less grip on snow",
            "Easier for beginners",
            "Less stable at high speed"
        ],
        "next_preview": {
            "title": "Quick Check: Skidding",
            "description": "Answer one question to lock in what you just learned.",
            "icon": "step-icon-quiz"
        },
        "prev": "/learn/1",
        "next": "/quiz/2"
    },
    "3": {
        "id": "3",
        "title": "What is Carving?",
        "media_type": "video",
        "media_url": "/static/videos/learn_3.mp4",
        "points": [
            "Board edge cuts into snow",
            "Smooth curved motion",
            "More control at speed",
            "Clean and efficient"
        ],
        "next_preview": {
            "title": "Quick Check: Carving",
            "description": "Test what carving is best for before moving on.",
            "icon": "step-icon-quiz"
        },
        "prev": "/quiz/2",
        "next": "/quiz/3"
    },
    "4": {
        "id": "4",
        "title": "Carve vs Skidded Turns",
        "media_type": "video",
        "media_url": "/static/videos/learn_4.mp4",
        "points": [
            "Skidding -> messy, wide tracks",
            "Carving -> thin, clean lines"
        ],
        "hint": "Looking at tracks is the best way to tell which is which!",
        "next_preview": {
            "title": "Quick Check: Spot the Turn",
            "description": "Identify carving vs skidding from position and tracks.",
            "icon": "step-icon-quiz"
        },
        "prev": "/quiz/1",
        "next": "/quiz/4"
    },
    "5": {
        "id": "5",
        "title": "Scenario: Losing Control! How to Control Speed",
        "media_type": "video",
        "media_url": "/static/videos/learn_5.mp4",
        "points": [
            "Scenario: You are riding down a steep slope, speed is increasing, and you feel out of control."
        ],
        "question": "What should you use?",
        "options": ["A. Skidding", "B. Carving"],
        "answer": "A. Skidding",
        "feedback": "Correct! Skidding increases friction to help you slow down.",
        "next_preview": {
            "title": "Final Question",
            "description": "One last check on what you'd do in this scenario.",
            "icon": "step-icon-quiz"
        },
        "prev": "/quiz/4",
        "next": "/quiz/5"
    }
}

quiz_content = {
    "1": {
        "id": "1",
        "q": "Main difference between carving and skidding?",
        "options": ["Speed", "Edge vs sliding", "Equipment"],
        "a": "Edge vs sliding",
        "prev": "/quiz/3",
        "next": "/learn/4"
    },
    "2": {
        "id": "2",
        "q": "Which technique is easier for beginners?",
        "options": ["Carving", "Skidding"],
        "a": "Skidding",
        "prev": "/learn/2",
        "next": "/learn/3"
    },
    "3": {
        "id": "3",
        "q": "Which technique gives more control at high speeds?",
        "options": ["Skidding", "Carving"],
        "a": "Carving",
        "prev": "/learn/3",
        "next": "/quiz/1"
    },
    "4": {
        "id": "4",
        "q": "Which snowboard track shows a carving arc?",
        "options": ["Left track", "Right track"],
        "a": "Left track",
        "media": "/static/data/carving-track-comparison.png",
        "tip_title": "Compare the two arcs",
        "tip_desc": "Focus on the shape and texture of each snowboard track before choosing your answer.",
        "prev": "/learn/4",
        "next": "/learn/5"
    },
    "5": {
        "id": "5",
        "q": "How can you tell someone is carving by tracks?",
        "options": ["Wide messy tracks", "Thin clean tracks"],
        "a": "Thin clean tracks",
        "prev": "/learn/5",
        "next": "/results"
    }
}

# Display order for quizzes — drives "Question X of N" and the progress bar.
QUIZ_ORDER = ["2", "3", "1", "4", "5"]


def reset_session():
    user_data["score"] = 0
    user_data["results"] = {}
    user_data["score_attempt"] = 0
    user_data["results_attempt"] = {}
    user_data["learn_enter_time"] = {}
    user_data["learn_stay_time"] = {}


def reset_attempt():
    user_data["score_attempt"] = 0
    user_data["results_attempt"] = {}


@app.route('/')
def home():
    session['quiz_mode'] = 'normal'
    session['current_attempt_score'] = 0
    session.pop('attempt_results', None) 
    return render_template('home.html')



@app.route('/learn/<id>')
def learn(id):
    content = learning_content.get(id)
    if content is None:
        abort(404)

    user_data.setdefault("learn_enter_time", {})
    user_data.setdefault("learn_stay_time", {})

    lesson_id = int(id)
    user_data["learn_enter_time"][lesson_id] = time.time()

    lesson = {
        "title": content.get("title", ""),
        "lesson_id": lesson_id,
        "media": content.get("media_url", ""),
        "note": content.get("note", ""),
        "text": " ".join(content.get("points", [])),
        "next_preview": content.get("next_preview"),
        "prev_url": content.get("prev", ""),
        "next_url": content.get("next", "/results"),
    }

    return render_template('learn.html', lesson=lesson)


@app.route('/learn/last_page', methods=["POST"])
def learn_last_page():
    req = request.get_json(silent=True) or {}
    lesson_id = req.get("id")

    if lesson_id is None:
        return jsonify(success=False, error="Missing lesson id"), 400

    try:
        lesson_id = int(lesson_id)
    except (TypeError, ValueError):
        return jsonify(success=False, error="Invalid lesson id"), 400

    enter_time = user_data.get("learn_enter_time", {}).get(lesson_id)
    if enter_time is None:
        return jsonify(success=True, recorded=False)

    user_data.setdefault("learn_stay_time", {})
    user_data["learn_stay_time"][lesson_id] = time.time() - enter_time

    return jsonify(success=True, recorded=True)


@app.route('/quiz/<id>')
def quiz(id):
    if id == QUIZ_ORDER[0]:
        reset_attempt()

    content = quiz_content.get(id)
    if content is None:
        abort(404)

    if id == QUIZ_ORDER[0]:
        reset_attempt()

    try:
        position = QUIZ_ORDER.index(id) + 1
    except ValueError:
        position = int(id)

    if session.get('quiz_mode') == 'retake':
        try:
            curr_idx = QUIZ_ORDER.index(id)
            if curr_idx < len(QUIZ_ORDER) - 1:
                next_url = "/quiz/" + QUIZ_ORDER[curr_idx + 1]
            else:
                next_url = "/results"
            
            if curr_idx > 0:
                prev_url = "/quiz/" + QUIZ_ORDER[curr_idx - 1]
            else:
                prev_url = ""
        except ValueError:
            next_url = "/results"
            prev_url = ""
    else:
        next_url = content.get("next", "/results")
        prev_url = content.get("prev", "")

    question = {
        "quiz_id": content.get("id", id),
        "question_number": position,
        "total_questions": len(QUIZ_ORDER),
        "question": content.get("q", ""),
        "options": content.get("options", []),
        "media": content.get("media", ""),
        "tip_title": content.get("tip_title", "Choose the best answer"),
        "tip_desc": content.get("tip_desc", "Think about what you've learned so far. You've got this!"),
        "prev_url": prev_url,
        "next_url": next_url,
    }
    return render_template('quiz.html', question=question)


@app.route('/record_answer', methods=['POST'])
def record_answer():
    req = request.get_json(silent=True) or {}
    quiz_id = req.get('quiz_id')
    user_answer = req.get('user_answer')

    if quiz_id not in quiz_content:
        return jsonify(success=False, error="Invalid quiz_id"), 400

    if 'attempt_results' not in session:
        session['attempt_results'] = {}

    attempt_results = session['attempt_results']

    is_correct = (user_answer == quiz_content[quiz_id]['a'])

    attempt_results[quiz_id] = is_correct
    session['attempt_results'] = attempt_results

    current_score = sum(1 for v in attempt_results.values() if v)
    session['current_attempt_score'] = current_score

    if quiz_id == QUIZ_ORDER[-1]: 
        session['last_final_score'] = session['current_attempt_score']
        session.pop('attempt_results', None)
        session.pop('current_attempt_score', None)
        session['quiz_mode'] = 'normal'

    return jsonify(success=True)




@app.route('/record', methods=['POST'])
def record():
    return record_answer()


@app.route('/retake')
def retake():
    session['quiz_mode'] = 'retake'
    session['current_attempt_score'] = 0
    session.pop('attempt_results', None) 
    first_quiz = QUIZ_ORDER[0]
    return redirect(url_for('quiz', id=first_quiz))


@app.route('/results')
def results():
    last_score = session.get('last_final_score', 0)
    return render_template('results.html', score=last_score, total=5)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)