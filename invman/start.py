import functools
from flask import Blueprint, render_template, request, url_for, flash, redirect, session, g
from invman.db import get_db

bp = Blueprint('start', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    error = None
    if g.user:
        return redirect(url_for('main.products'))
    if request.method == 'POST':
        if 'login' in request.form:
            business_id = request.form['registered_b_id']
            business = db.execute('SELECT * FROM business WHERE business_id = ?', (business_id,)).fetchone()
            if business:
                session.clear()
                session['user_id'] = business['business_id']
                g.user = get_db().execute('SELECT * FROM business WHERE business_id = ?', (business_id,)).fetchone()
                return redirect(url_for('main.products'))
            else:
                error = 'Incorrect ID'
            flash(error)
        elif 'register' in request.form:
            new_business_id = request.form['create_b_id']
            new_business_name = request.form['create_b_name']
            if new_business_id and new_business_name:
                business_exists = db.execute('SELECT * FROM business WHERE business_id = ?', (new_business_id,)).fetchone()
                if not business_exists:
                    db.execute('INSERT INTO business (business_id, business_name) VALUES (?, ?)', (new_business_id, new_business_name))
                    db.commit()
                    return redirect(url_for('start.created'))
                else:
                    error = 'Business ID already exists'
            else:
                error = 'Please enter a business ID and Name'
            flash(error)
    return render_template('index.html', title='Home')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM business WHERE business_id = ?', (user_id,)
        ).fetchone()

@bp.route('/created')
def created():
    return '<h5>Business Created</h5><br>You can now <a href="/">login</a>'

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('start.index'))

        return view(**kwargs)

    return wrapped_view
