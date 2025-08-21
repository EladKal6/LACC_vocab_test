from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
import os, json, random
import string

views = Blueprint('views', __name__)

QUIZ_DIR = os.path.join(os.path.dirname(__file__), 'static')
QUIZ_PREFIX = 'questions_'
QUIZ_SUFFIX = '.json'
QUIZ_QUESTIONS_PER_TEST = 4  # Change this value to set the number of questions per quiz

# Generate a fixed random code at startup
# PROLIFIC_COMPLETION_CODE = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
PROLIFIC_COMPLETION_CODE = "jAdgPWRlQPFvoCbc"


def list_quizzes():
	quizzes = []
	for fname in os.listdir(QUIZ_DIR):
		if fname.startswith(QUIZ_PREFIX) and fname.endswith(QUIZ_SUFFIX):
			quiz_id = fname[len(QUIZ_PREFIX):-len(QUIZ_SUFFIX)]
			quizzes.append({
				'id': quiz_id,
				'filename': fname,
				'title': f'Quiz {quiz_id}'
			})
	return quizzes

def load_easy_question_for_quiz(quiz_id: str):
	easy_path = os.path.join(QUIZ_DIR, 'easy_questions.json')
	if not os.path.exists(easy_path):
		return None
	try:
		with open(easy_path, 'r', encoding='utf-8') as f:
			all_easy = json.load(f)
		return all_easy.get(quiz_id)
	except Exception:
		return None

@views.route('/')
def home():
	quizzes = list_quizzes()
	return render_template('home.html', quizzes=quizzes)

@views.route('/start_quiz_session', methods=['GET', 'POST'])
def start_quiz_session():
	quizzes = list_quizzes()
	if len(quizzes) < 3:
		return "Not enough quizzes available.", 400
	selected = random.sample(quizzes, 3)
	main_quiz = random.choice(selected)
	others = [q for q in selected if q['id'] != main_quiz['id']]
	# Order: main, other1, main, other2, main
	quiz_sequence = [main_quiz['id'], others[0]['id'], main_quiz['id'], others[1]['id'], main_quiz['id']]
	session['quiz_sequence'] = quiz_sequence
	session['quiz_index'] = 0
	session['quiz_results'] = []
	session['used_question_ids'] = []
	return redirect(url_for('views.quiz_session'))

@views.route('/quiz_session', methods=['GET', 'POST'])
def quiz_session():
	quiz_sequence = session.get('quiz_sequence')
	quiz_index = session.get('quiz_index', 0)
	if not quiz_sequence or quiz_index >= len(quiz_sequence):
		return redirect(url_for('views.home'))
	quiz_id = quiz_sequence[quiz_index]
	quiz_file = os.path.join(QUIZ_DIR, f'{QUIZ_PREFIX}{quiz_id}{QUIZ_SUFFIX}')
	if not os.path.exists(quiz_file):
		return f"Quiz '{quiz_id}' not found.", 404
	with open(quiz_file, 'r', encoding='utf-8') as f:
		quiz_data = json.load(f)
	instructions = quiz_data.get('instructions', '')
	question_display = quiz_data.get('question_display', 'definition_prompt')
	all_questions = quiz_data.get('questions', [])
	# Track used question ids in session
	used_question_ids = set(session.get('used_question_ids', []))
	available_questions = [q for q in all_questions if q['id'] not in used_question_ids]
	count = min(QUIZ_QUESTIONS_PER_TEST, len(available_questions))
	questions = random.sample(available_questions, count)
	# Update used_question_ids in session
	used_question_ids.update(q['id'] for q in questions)
	session['used_question_ids'] = list(used_question_ids)
	easy_question = load_easy_question_for_quiz(quiz_id)
	quiz_title = f"Quiz: {quiz_id} ({quiz_index+1} of {len(quiz_sequence)})"
	return render_template(
		'questions.html',
		questions=questions,
		quiz_id=quiz_id,
		instructions=instructions,
		question_display=question_display,
		quiz_title=quiz_title,
		quizzes_left=len(quiz_sequence) - quiz_index,
		easy_question=easy_question
	)

@views.route('/quiz/<quiz_id>', methods=['GET', 'POST'])
def show_questions(quiz_id):
	quiz_file = os.path.join(QUIZ_DIR, f'{QUIZ_PREFIX}{quiz_id}{QUIZ_SUFFIX}')
	if not os.path.exists(quiz_file):
		return f"Quiz '{quiz_id}' not found.", 404
	with open(quiz_file, 'r', encoding='utf-8') as f:
		quiz_data = json.load(f)
	instructions = quiz_data.get('instructions', '')
	question_display = quiz_data.get('question_display', 'definition_prompt')
	all_questions = quiz_data.get('questions', [])
	count = min(QUIZ_QUESTIONS_PER_TEST, len(all_questions))
	questions = random.sample(all_questions, count)
	easy_question = load_easy_question_for_quiz(quiz_id)
	return render_template(
		'questions.html',
		questions=questions,
		quiz_id=quiz_id,
		instructions=instructions,
		question_display=question_display,
		easy_question=easy_question
	)

# Dynamic submit endpoint
@views.route('/submit_quiz/<quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
	data = request.get_json()
	results = data.get('results', [])
	score = data.get('score', 0)
	user_id = request.remote_addr
	# Record session with quiz_id
	current_app.quiz_answers.record_session(
		user_id=user_id,
		question_results=results,
		score=score
	)
	# Return JSON for frontend
	return jsonify({'status': 'ok', 'session_id': str(user_id), 'quiz_id': quiz_id})

@views.route('/submit_quiz_part', methods=['POST'])
def submit_quiz_part():
	data = request.get_json()
	quiz_id = data.get('quiz_id')
	results = data.get('results', [])
	score = data.get('score', 0)
	# Persist results server-side to avoid oversized session cookies
	from uuid import uuid4
	from datetime import datetime
	user_id = request.remote_addr
	session_id = session.get('db_session_id')
	if not session_id:
		session_id = str(uuid4())
		session['db_session_id'] = session_id
	quiz_sequence = session.get('quiz_sequence', [])
	current_app.quiz_answers.service.collection.update_one(
		{'session_id': session_id},
		{
			'$setOnInsert': {
				'session_id': session_id,
				'user_id': user_id,
				'timestamp': datetime.utcnow(),
				'quiz_sequence': quiz_sequence
			},
			'$push': {
				'results': {
					'quiz_id': quiz_id,
					'results': results,
					'score': score
				}
			}
		},
		upsert=True
	)
	# Maintain only minimal client-side state
	session['quiz_results'] = []
	session['quiz_index'] = session.get('quiz_index', 0) + 1
	quiz_sequence = session.get('quiz_sequence', [])
	quiz_index = session['quiz_index']
	if quiz_index < len(quiz_sequence):
		return jsonify({'next_quiz_url': url_for('views.quiz_session')})
	else:
		return jsonify({'finish_url': url_for('views.quiz_finish')})

@views.route('/quiz_finish')
def quiz_finish():
	user_id = request.remote_addr
	quiz_sequence = session.get('quiz_sequence', [])
	quiz_results = session.get('quiz_results', [])
	demographics = session.get('demographics', {})
	from datetime import datetime
	# Mark completion on the server-side document if present
	db_session_id = session.get('db_session_id')
	if db_session_id:
		current_app.quiz_answers.service.collection.update_one(
			{'session_id': db_session_id},
			{'$set': {
				'demographics': demographics,
				'completed_at': datetime.utcnow()
			}}
		)
	else:
		# Fallback: insert if no server-side session doc exists
		session_doc = {
			'user_id': user_id,
			'timestamp': datetime.utcnow(),
			'quiz_sequence': quiz_sequence,
			'results': quiz_results,
			'demographics': demographics
		}
		current_app.quiz_answers.service.collection.insert_one(session_doc)
	# Clear session state
	session.pop('quiz_sequence', None)
	session.pop('quiz_index', None)
	session.pop('quiz_results', None)
	session.pop('used_question_ids', None)
	session.pop('demographics', None)
	session.pop('db_session_id', None)
	return render_template('finish.html', completion_code=PROLIFIC_COMPLETION_CODE)

@views.route('/pre_quiz_info', methods=['GET', 'POST'])
def pre_quiz_info():
	if request.method == 'POST':
		# Save demographic data in session
		session['demographics'] = {
			'name': request.form.get('name', ''),
			'age': request.form.get('age', ''),
			'country': request.form.get('country', ''),
			'native_language': request.form.get('native_language', ''),
			'other_languages': request.form.get('other_languages', ''),
			'english_level': request.form.get('english_level', '')
		}
		return redirect(url_for('views.start_quiz_session'))
	return render_template('pre_quiz_info.html')