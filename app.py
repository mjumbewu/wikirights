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
    user_input = user_data['session']['initialText']
    user_id = user_data['session']['from']['id']
    
    conv = get_conversation(user_id)
    
    if conv is None:
        return start_conversation(user_id, user_input)
    
    else:
        return continue_conversation(user_id, conv['topics'], user_input)


def start_conversation(user_id, search_terms):
    topics = resolve_topics(search_terms)
    
    if len(topics) == 1:
        response = "You asked for %s: %s" % (topics[0]['title'], topics[0]['text'])
    elif len(topics) > 1:
        response = 'Did you mean:'
        choice = 0
        for topic in topics:
            choice += 1
            response += '\n%d. "%s"' % (choice, topic['title'])
            
        store_conversation(user_id, topics)
    else:
        response = "I didn't understand you; please try again"
    
    # What should I expect (what legal action can others take)
    # Legal action can I take
    # Who can I contact to get help
    
    phone = Tropo()
    phone.say(response)
    return (phone.RenderJson(), 200, {'content-type': 'application/json'})


def continue_conversation(user_id, topics, choice):
    if choice in topics:
        response = "You asked for %s: %s" % (topics[choice]['title'], topics[choice]['text'])
    else:
        clear_conversation(user_id)
        return start_conversation(user_id, choice)
    
    phone = Tropo()
    phone.say(response)
    return (phone.RenderJson(), 200, {'content-type': 'application/json'})
    

def store_conversation(user_id, topics):
    """
    Remember (store in the database) that we asked the user to choose from the
    given topics.
    """
    pass


def get_conversation(user_id):
    """
    Retrieve the topics that we asked the user to choose from, or return None
    if we haven't aksed for anything from the user.
    """
    pass


def clear_conversation(user_id):
    """
    Clear the record of a conversation with the user.
    """
    pass
    

def resolve_topics(terms):
    """
    Take a search string and return a set of topics that might match for the
    query.
    """
    # search for terms in the db
    # return matching strings
    topics = [
        {
            "title": "What if I didn't get paid",
            "text": "Some information about what to do if you didn't get paid"
        },
        {
            "title": "What if I am injured on the job",
            "text": "Some information about what to do if you were injured on the job"
        },
        {
            "title": "What if I got fired",
            "text": "Some information about what to do if you got fired"
        },
        {
            "title": "What if I quit",
            "text": "Some information about what to do if you quit your job"
        },
    ]
    
    matching_topics = []
    for topic in topics:
        if are_similar(topic['title'], terms):
            matching_topics.append(topic)
    
    return matching_topics


def are_similar(string1, string2):
    return (string1 in string2) or (string2 in string1)


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
