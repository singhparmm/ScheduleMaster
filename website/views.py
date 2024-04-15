from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from sqlalchemy import func


from datetime import datetime, timedelta
import calendar
from calendar import monthrange, day_name
from flask import request
from dateutil.relativedelta import relativedelta



from flask import render_template
from flask import Flask, request, jsonify, flash, redirect, url_for




views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note_content = request.form.get('note')
        note_date = request.form.get('date')  # Assume date is passed as 'YYYY-MM-DD'
        note_hour = request.form.get('hour')  # Assume hour is passed as an integer from 0 to 23

        if len(note_content) < 1:
            flash('Note is too short!', category='error')
        else:
            try:
                full_date = datetime.strptime(note_date + f' {note_hour}:00', '%Y-%m-%d %H:%M')
                new_note = Note(data=note_content, user_id=current_user.id, date=full_date)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')
            except ValueError as e:
                flash('Invalid date or time format', category='error')
                print(e)  # For debugging

    # Adjust query to include notes for today, even if past current time
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    notes = Note.query.filter(Note.user_id == current_user.id, Note.date >= now).order_by(Note.date.asc()).all()
    return render_template("home.html", user=current_user, notes=notes)




@views.route('/day-detail')
@login_required
def day_detail():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    notes = Note.query.filter(func.date(Note.date)==date, Note.user_id==current_user.id).all()
    return render_template("day_detail.html", date=date_str, notes=notes, user=current_user)


@views.route('/weekly')
@login_required
def weekly_view():
    today = datetime.now()
    offset = request.args.get('offset', default=0, type=int)
    start_of_week = (today - timedelta(days=today.weekday()) + timedelta(weeks=offset)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = (start_of_week + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    notes = Note.query.filter(Note.user_id == current_user.id, 
                              Note.date >= start_of_week, 
                              Note.date <= end_of_week).order_by(Note.date.asc(), Note.hour.asc()).all()
    
    dates_with_days = [
        ((start_of_week + timedelta(days=i)).strftime("%A"),
         (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
        for i in range(7)
    ]

    next_week_offset = offset + 1
    prev_week_offset = offset - 1
    
    return render_template("week_view.html", user=current_user, dates_with_days=dates_with_days, notes=notes, next_week_offset=next_week_offset, prev_week_offset=prev_week_offset)


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



# @app.route('/update_note', methods=['POST'])
# @login_required
# def update_note():
#     note_id = request.form.get('note_id')
#     new_content = request.form.get('new_content')
#     new_date = request.form.get('new_date')
#     new_hour = request.form.get('new_hour')
#     note = Note.query.get(note_id)
    
#     if note and note.user_id == current_user.id:
#         note.data = new_content
#         note.date = datetime.strptime(new_date, '%Y-%m-%d')
#         note.hour = int(new_hour)
#         db.session.commit()
#         flash('Note updated successfully!', category='success')
#         return redirect(url_for('home'))
#     else:
#         flash('Error updating note.', category='error')
#         return redirect(url_for('home'))
