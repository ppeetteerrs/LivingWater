from flask import jsonify
from flask import request
from flask_cors import CORS

from . import app
from ..backend.intelligence.api import API
from ...tools.exceptions import DebugException

CORS(app)


@app.route('/get_rankings')
def get_rankings():
    try:
        sentence = request.args.get('sentence')
        response = API.get_rankings(sentence=sentence)
        return jsonify(response)
    except DebugException as e:
        return str(e), 401


@app.route('/vote')
def vote():
    try:
        json_string = request.args.get('json_string')
        positive = request.args.get('positive')
        print("Voted for item", json_string)
        print("Positive:", positive)
        response = API.vote(json_string, positive)
        return jsonify(response)
    except DebugException as e:
        return str(e), 401


@app.route('/get_synonyms')
def get_synonyms():
    try:
        base_word = request.args.get('base_word')
        response = API.get_synonyms(base_word)
        return jsonify(response)
    except DebugException as e:
        return str(e), 401


@app.route('/modify_synonyms')
def modify_synonyms():
    try:
        json_string = request.args.get('json_string')
        response = API.modify_synonym(json_string)
        return jsonify(response)
    except DebugException as e:
        return str(e), 401


@app.route('/modify_related_words')
def modify_related_words():
    try:

        json_string = request.args.get('json_string')
        print("Modifying related words")
        response = API.modify_related_words(json_string)
        return jsonify(response)
    except DebugException as e:
        return str(e), 401


@app.route('/reset_secrett')
def reset():
    try:
        return jsonify(API.reset_votes())
    except DebugException as e:
        return str(e), 401


@app.route('/search_verse')
def search():
    try:
        query_string = request.args.get('query_string')
        return jsonify(API.search_verse(query_string))
    except DebugException as e:
        return str(e), 401


@app.route('/edit_link')
def edit_link():
    try:
        json_string = request.args.get('json_string')
        return jsonify(API.edit_link(json_string))
    except DebugException as e:
        return str(e), 401


@app.route('/update_verse')
def update_verse_location():
    try:
        old_location = request.args.get('old_location')
        new_location = request.args.get('new_location')
        return jsonify(API.update_verse_location(old_location, new_location))
    except DebugException as e:
        return str(e), 401


@app.route('/add_verse')
def add_verse():
    try:
        json_string = request.args.get('json_string')
        return jsonify(API.add_verse(json_string))
    except DebugException as e:
        return str(e), 401


@app.route('/remove_verse')
def remove_verse():
    try:
        location = request.args.get('location')
        return jsonify(API.remove_verse(location))
    except DebugException as e:
        return str(e), 401


@app.route('/add_word')
def add_word():
    try:
        new_word = request.args.get('new_word')
        copy = request.args.get('copy')
        return jsonify(API.add_word(new_word, copy))
    except DebugException as e:
        return str(e), 401


@app.route('/delete_word')
def delete_word():
    try:
        word = request.args.get('word')
        return jsonify(API.delete_word(word))
    except DebugException as e:
        return str(e), 401
