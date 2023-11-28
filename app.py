import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Global variable
connection_tally = int()

# Logging
def setup_logger():
    stdout_handler = logging.StreamHandler(stream=sys.stdout) 
    stderr_handler = logging.StreamHandler(stream=sys.stderr) 
    handlers = [stdout_handler, stderr_handler ]
#    format_output = '%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p' 
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG, handlers =handlers)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_tally
    connection_tally += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    app.logger.info('Page retrieved.')
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'




# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)
	
# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.warning('Page not found.')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page has been retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            app.logger.info('Article %s created!', title)
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the status endpoint of the web application
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Healthz status request successfull.')
    return response


@app.route('/metrics')
def metrics():
    with get_db_connection() as conn:
        global connection_tally
        cursor = None
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM posts')
            posts = cursor.fetchone()[0]
            jdata = {'db_connection_count': connection_tally, 'post_count': posts}
            response = app.response_class(
                response=json.dumps(jdata), status=200, mimetype='application/json')
            app.logger.info('Metrics request successfull.')
            return response
        finally:
            if cursor:
                cursor.close()




# start the application on port 3111
if __name__ == "__main__":
  setup_logger()
# Define the logging policy
#  logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)
  
  app.run(host='0.0.0.0', port='3111')