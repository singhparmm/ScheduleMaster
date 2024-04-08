from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json


from datetime import datetime, timedelta
import calendar
from calendar import monthrange, day_name
from flask import request
from dateutil.relativedelta import relativedelta




views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note) 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/day-detail')
@login_required
def day_detail():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    notes = Note.query.filter_by(date=date, user_id=current_user.id).all()
    return render_template("day_detail.html", date=date_str, notes=notes, user=current_user)


@views.route('/weekly')
@login_required
def weekly_view():
    today = datetime.now()
    offset = request.args.get('offset', default=0, type=int)
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    
    dates_with_days = [
    ((start_of_week + timedelta(days=i)).strftime("%A"),
     (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
    for i in range(7)
    ]    

    next_week_offset = offset + 1
    prev_week_offset = offset - 1
    
    return render_template("week_view.html", user=current_user, dates_with_days=dates_with_days, next_week_offset=next_week_offset, prev_week_offset=prev_week_offset)


@views.route('/monthly')
@login_required
def monthly_view():
    offset = request.args.get('offset', default=0, type=int)
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    target_month = first_day_of_current_month + relativedelta(months=offset)
    days_in_month = monthrange(target_month.year, target_month.month)[1]

    placeholders_before = (target_month.weekday() + 1) % 7
    days = [''] * placeholders_before

    for day in range(1, days_in_month + 1):
        full_date = datetime(target_month.year, target_month.month, day).strftime('%Y-%m-%d')
        days.append(full_date) 
    placeholders_after = 7 - ((len(days) % 7) or 7)
    days.extend([''] * placeholders_after)

    return render_template("month_view.html", days=days, current_month=target_month.strftime("%B"), current_year=target_month.year, next_month_offset=offset + 1, prev_month_offset=offset - 1, user=current_user)



@views.route('/yearly')
@login_required
def yearly_view():
    today = datetime.now()
    current_year = today.year
    months_with_offsets = []
    for i in range(1, 13):
        month_date = datetime(current_year, i, 1)
        offset = (month_date.year - today.year) * 12 + month_date.month - today.month
        months_with_offsets.append((month_date.strftime("%B"), offset))
    
    return render_template("year_view.html", user=current_user, year=current_year, months_with_offsets=months_with_offsets)



@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/add_note', methods=['POST'])
def add_note():
    date = request.json['date']
    hour = request.json['hour']
    content = request.json['content']
    note_date = datetime.strptime(date, '%Y-%m-%d').date()
    existing_note = Note.query.filter_by(date=note_date, hour=hour, user_id=current_user.id).first()
    if existing_note:
        existing_note.data = content
        db.session.commit()
        return jsonify({'message': 'Note updated successfully'})
    else:
        note = Note(date=note_date, hour=hour, data=content, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        return jsonify({'message': 'Note added successfully'})

@views.route('/get_notes', methods=['POST'])
def get_notes():
    date = request.json.get('date')
    notes = Note.query.filter_by(date=date, user_id=current_user.id).all()
    return jsonify({'notes': [{'id': note.id, 'data': note.data} for note in notes]})