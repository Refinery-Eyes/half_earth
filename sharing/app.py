import json
from gen_id import gen_id
from gen_image import gen_image
from summarize import summarize
from flask_cors import CORS
from flask import Flask, request, redirect, jsonify, render_template, send_from_directory, url_for
from badges import BADGES
from db import db, save_session, get_session

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return redirect('https://half.earth/')
    else:
        data = request.get_json()
        if data is None:
            return jsonify(success=False)
        summary = summarize(data)
        id = gen_id()
        img_path = 'uploads/{}.jpg'.format(id)
        gen_image(
                data['world']['year'],
                summary,
                img_path)
        save_session(id, summary)

        badges = [{
            'name': b,
            'desc': BADGES[b]['desc']
        } for b in summary['badges']]
        return jsonify(
                success=True,
                badges=badges,
                image=url_for('image', fname='{}.jpg'.format(id), _external=True),
                url=url_for('summary', id=id, _external=True))

@app.route('/img/<fname>')
def image(fname):
    return send_from_directory('uploads', fname)

@app.route('/<id>')
def summary(id):
    session = get_session(id)
    summary = json.loads(session.data)
    fname = '{}.jpg'.format(id)
    badges = [{
        'name': b,
        'desc': BADGES[b]['desc']
    } for b in summary['badges']]
    return render_template('summary.html',
            summary=summary, badges=badges,
            img_fname=fname)

if __name__ == '__main__':
    app.run()
