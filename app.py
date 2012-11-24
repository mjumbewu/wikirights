"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from tropo import Tropo
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/sms-query', methods=['GET', 'POST'])
def sms_query():
    user_data = json.loads(request.data)
    search_terms = user_data['initialText']
    # "i didn't get paid"
    
    topics = resolve_topics(search_terms)
    
    if topics:
        response = 'Did you mean:'
        choice = 0
        for topic in topics:
            choice += 1
            response += '\n%d. "%s"' % (choice, topic)
    else:
        response = "I didn't understand you; please try again"
    
    # what action you can take
    # who to contact to get help
    
    phone = Tropo()
    phone.say(response)
    return (phone.RenderJson(), 200, {'content-type': 'application/json'})
    
    
def resolve_topics(terms):
    """
    Take a search string and return a set of topics that might match for the
    query.
    """
    return ["I didn't get paid", "I got injured"]


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
