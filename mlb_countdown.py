# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/Users/drewdez/Documents/web_projects/mlb_countdown/mlb_countdown.sqlite'
DEBUG = True
SECRET_KEY = 'development key'
#USERNAME = 'admin'
#PASSWORD = 'default'

# create our little application
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
	#return('/' + request.form['team'])
	cur = g.db.execute('select teamabbr, teamfull from Dates order by teamfull')
	teamData = [dict(abbr=row[0], full=row[1]) for row in cur.fetchall()]
	return render_template('select_team.html', teams=teamData)
	#return redirect('/' + request.form['team'])

@app.route('/<team>', methods=['POST'])
def show_countdown2(team):
	#cur = g.db.execute('select * from Dates where teamabbr = (?)', LAD)
	#return render_template('countdown.html')
	return request.form['team']

@app.route('/countdown')
def show_countdown():
	cur = g.db.execute('select * from Dates where teamabbr = (?)', [request.args.get('team')])
	#cur = g.db.execute('select * from Dates')
	#teamData = [dict(abbr=row[0], full=row[1], nickname=row[2]) for row in cur.fetchall()]
	data = cur.fetchone()
	teamData = dict(abbr=data[0], full=data[1], nickname=data[2], pcReport=data[3],
		exOpener=data[4], rsOpener=data[5], background_color=data[6], text_color=data[7])
	#abbr = cur.fetchone().row[0]
	#full = cur.fetchone().row[1]
	#nickname = cur.fetchone().row[2]
	#for team in team:
	#	return 'test'
	#return teamData.teamFull
	#return cur.fetchone()
	#for row in cur.fetchall():
	#	return (row[0] + row[1] + row[2])
	#return render_template('countdown.html')
	return render_template('countdown.html', team=teamData)
	#return request.args.get('team')

if __name__ == '__main__':
	app.run(debug=True)