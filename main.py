# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request, session, Response
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
from datetime import datetime
import os
import time
from utils import *
from voiceTest import *

app = Flask(__name__)
app.secret_key = 'parkisense_secret_2024'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True


def init_db():
    """Create all required tables and runtime folders on startup."""
    con = sqlite3.connect('mydatabase.db')
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FinalPred (
            Date text, Name text, DrawingPrediction text,
            VoicePrediction text, FinalPrediction text
        )
    """)
    con.commit()
    con.close()
    os.makedirs('static/img', exist_ok=True)
    os.makedirs('upload', exist_ok=True)
    print("DEBUG: Database initialised.")

init_db()


@app.context_processor
def inject_now():
	return {
		'now': datetime.now(),
		'timestamp': int(time.time()),
		'name': session.get('name', 'Guest')
	}


# ── Landing page → directly to home (no login needed) ────────────────────────
@app.route('/')
def landing():
	# Set a default guest name so templates work
	if 'name' not in session:
		session['name'] = 'Guest'
		session['pred'] = 'Healthy'
		session['voicePred'] = 'Healthy'
	return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
	if 'name' not in session:
		session['name'] = 'Guest'
		session['pred'] = 'Healthy'
		session['voicePred'] = 'Healthy'
	return render_template('home.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	user_name = session.get('name', 'Guest')
	pred = session.get('pred', 'Healthy')
	voicePred = session.get('voicePred', 'Healthy')

	if pred == 'Parkinson' and voicePred == 'Parkinson':
		final = 'Weak Pattern'
	elif pred == 'Healthy' and voicePred == 'Healthy':
		final = 'Healthy'
	else:
		final = 'Further Diagnosis is Required'

	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

	try:
		con = sqlite3.connect('mydatabase.db')
		cursor = con.cursor()
		cursor.execute("INSERT INTO FinalPred VALUES(?,?,?,?,?)",
		               (dt_string, user_name,
		                "Weak Pattern" if pred == 'Parkinson' else pred,
		                "Weak Pattern" if voicePred == 'Parkinson' else voicePred,
		                final))
		con.commit()
		conn = sqlite3.connect('mydatabase.db', isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
		df = pd.read_sql_query("SELECT * from FinalPred WHERE Name=?", conn, params=(user_name,))
		conn.close()
	except Exception as e:
		print(f"DEBUG: Dashboard DB error: {e}")
		import pandas as pd
		df = pd.DataFrame(columns=['Date', 'Name', 'DrawingPrediction', 'VoicePrediction', 'FinalPrediction'])

	now_date = now.strftime("%d %B %Y, %H:%M")
	return render_template('dashboard.html',
	                       tables=[df.to_html(classes='table-responsive table table-bordered table-hover')],
	                       titles=df.columns.values, now_date=now_date)


@app.route('/image', methods=['GET', 'POST'])
def image():
	if 'name' not in session:
		session['name'] = 'Guest'
		session['pred'] = 'Healthy'
		session['voicePred'] = 'Healthy'
	if request.method == 'POST':
		savepath = r'static/img/'
		os.makedirs(savepath, exist_ok=True)

		# Check for base64 drawing data
		drawing_data = request.form.get('drawing_data')
		if drawing_data and ',' in drawing_data:
			import base64
			try:
				header, encoded = drawing_data.split(",", 1)
				data = base64.b64decode(encoded)
				with open(os.path.join(savepath, 'test.jpg'), 'wb') as f:
					f.write(data)
				return redirect(url_for('image_test'))
			except Exception as e:
				print(f"DEBUG: Error saving canvas drawing: {e}")

		# Check for file upload
		f = request.files.get('doc')
		if f:
			f.save(os.path.join(savepath, secure_filename('test.jpg')))
			return redirect(url_for('image_test'))
	return render_template('image.html')


@app.route('/image_test', methods=['GET', 'POST'])
def image_test():
	label, result, suggestion, accuracy = predictImg(r'static/img/test.jpg')
	if label is not None:
		session['pred'] = label
	return render_template('image_test.html', result=result, suggestion=suggestion, confidence=accuracy)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if 'name' not in session:
		session['name'] = 'Guest'
		session['pred'] = 'Healthy'
		session['voicePred'] = 'Healthy'
	if request.method == 'POST':
		if request.form.get('uploadbutton') == 'Upload':
			savepath = r'upload/'
			os.makedirs(savepath, exist_ok=True)
			f = request.files.get('doc')
			if f:
				f.save(os.path.join(savepath, secure_filename('test.wav')))
				return render_template('upload.html', file=f.filename, mgs='File uploaded..!!')
		elif request.form.get('uploadbutton') == 'Detect PD':
			voice_result = testVoice()
			if len(voice_result) == 2:
				_, msg = voice_result
				return render_template('upload.html', mgs=msg, accuracy=None)
			label, result, accuracy = voice_result
			session['voicePred'] = label
			return render_template('upload.html', mgs=result, accuracy=accuracy)
	return render_template('upload.html')


@app.route('/record', methods=['GET', 'POST'])
def record():
	if 'name' not in session:
		session['name'] = 'Guest'
	return render_template('record.html')


# Keep login/register/logout routes but they just redirect to home now
@app.route('/login', methods=['GET', 'POST'])
def login():
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	return redirect(url_for('home'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	return redirect(url_for('home'))


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
