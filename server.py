import asyncio
import datetime
import json
import traceback
import logging
import sys

from flask import Flask, render_template, request
from flask_restful import Resource, Api

from sticker import Sticker
import webex

from db import Database

app = Flask(__name__, template_folder="templates")
app.logger.setLevel(logging.DEBUG)
api = Api(app)

logging.getLogger('asyncio').setLevel(logging.CRITICAL)

@app.route('/visitors')
def visitors():
    with Database('visitors.db') as db:
        data = db.visitors()
        return render_template('/visitors.j2', data=data)

@app.template_filter('convert_date')
def convert_date(s):
    return datetime.datetime.fromtimestamp(s)

with open('config.json') as f:
    config = json.load(f)

def format_date(time):
    month = time.strftime('%B')
    return f"{month} {time.day}, {time.year}"

class StickerPrinter(Resource):
    def __init__(self):
        self.sticker = Sticker(config['printCommand'])

    def post(self):
        data = request.json
        app.logger.info(request.json)

        if not data:
            return { 'error': 'Not a valid JSON payload' }, 400

        field_errors = []
        for field in ['name', 'company', 'host', 'email', 'days']:
            if field not in data:
                field_errors.append(f"missing \"{field}\"")

        if 'date' in data:
            try:
                date = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                field_errors.append("date does not match format YYYY-MM-DD")
        else:
            date = datetime.datetime.now()

        if len(field_errors) > 0:
            error = f"Invalid payload: {', '.join(field_errors)}"
            return { 'error': error }, 400

        data['date'] = format_date(date)
        data['location'] = "LYSAKER 1"

        try:
            self.sticker.create(data)
            app.logger.info('printed OK')

            with Database('visitors.db') as db:
                db.insert(
                    data['name'],
                    data['company'],
                    data['host'],
                    data['email'],
                    data['days']
                )

            return {
                'success': True
            }, 200
        except Exception as exception:
            app.logger.error(exception)
            app.logger.error(traceback.format_exc())
            return {
                'error': str(exception),
                'details': traceback.format_exc()
            }, 500


class Ping(Resource):
    def get(self):
        return { 'success': True }, 200

class Webex(Resource):
    def get(self):
        if request.args:
            name = request.args['name']
            print('search for', name)
            return asyncio.run(webex.searchForPerson(name))
        else:
            return { 'success': False }, 400

    def post(self):
        message = request.json
        return asyncio.run(webex.sendMessage(message))

api.add_resource(StickerPrinter, '/')
api.add_resource(Ping, '/ping')
api.add_resource(Webex, '/webex')

if __name__ == '__main__':
    sticker = Sticker(config['printCommand'])
    sticker.dry_run = True
    app.run(debug=True)
else:
    app.debug = True
