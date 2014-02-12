# imports
import sqlite3
from flask import Flask, request, g, url_for, render_template
from contextlib import closing

# configuration
DATABASE = 'mlb_countdown.sqlite'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('populate_db.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def select_team():
	cur = g.db.execute('select teamabbr, teamfull from Dates order by teamfull')
	teamData = [dict(abbr=row[0], full=row[1]) for row in cur.fetchall()]
	return render_template('select_team.html', teams=teamData)

@app.route('/countdown')
def show_countdown():
	cur = g.db.execute('select * from Dates where teamabbr = (?)', [request.args.get('team')])
	data = cur.fetchone()
	teamData = dict(abbr=data[0], full=data[1], nickname=data[2], pcReport=data[3],
		exOpener=data[4], rsOpener=data[5], background_color=data[6], text_color=data[7])
	return render_template('countdown.html', team=teamData)

if __name__ == '__main__':
	app.run()