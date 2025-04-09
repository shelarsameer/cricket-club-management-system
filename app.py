from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Association Tables
player_team = db.Table('player_team',
    db.Column('player_id', db.Integer, db.ForeignKey('player.player_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.team_id'), primary_key=True)
)

team_match = db.Table('team_match',
    db.Column('team_id', db.Integer, db.ForeignKey('team.team_id'), primary_key=True),
    db.Column('match_id', db.Integer, db.ForeignKey('match.match_id'), primary_key=True)
)

# Models
class Player(db.Model, UserMixin):
    __tablename__ = 'player'
    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    contact = db.Column(db.String(20))
    role = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    memberships = db.relationship('Membership', backref='player', lazy=True)
    scorecards = db.relationship('Scorecard', backref='player', lazy=True)
    teams = db.relationship('Team', secondary=player_team, backref='players')

    def get_id(self):
        return str(self.player_id)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    __tablename__ = 'team'
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    coach = db.Column(db.String(100))
    captain_id = db.Column(db.Integer, db.ForeignKey('player.player_id'))
    matches = db.relationship('Match', secondary=team_match, backref='teams')

class Match(db.Model):
    __tablename__ = 'match'
    match_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))
    ground = db.Column(db.String(200))
    result = db.Column(db.String(50))
    scorecards = db.relationship('Scorecard', backref='match', lazy=True)

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    memberships = db.relationship('Membership', backref='admin', lazy=True)

    def get_id(self):
        return str(self.admin_id)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Membership(db.Model):
    __tablename__ = 'membership'
    member_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'))
    join_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    membership_type = db.Column(db.String(50))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'))

class Scorecard(db.Model):
    __tablename__ = 'scorecard'
    scorecard_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.match_id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'))
    runs = db.Column(db.Integer, default=0)
    wickets = db.Column(db.Integer, default=0)

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email/Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('admin', 'Admin'), ('player', 'Player')], validators=[DataRequired()])

class PlayerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(max=20)])
    role = StringField('Role', validators=[DataRequired(), Length(max=50)])

class MatchForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    ground = StringField('Ground', validators=[DataRequired(), Length(max=200)])
    result = SelectField('Result', choices=[
        ('', 'Select Result'),
        ('Team 1 Won', 'Team 1 Won'),
        ('Team 2 Won', 'Team 2 Won'),
        ('Draw', 'Draw'),
        ('Not Played', 'Not Played')
    ])
    team1 = SelectField('Team 1', coerce=int, validators=[DataRequired()])
    team2 = SelectField('Team 2', coerce=int, validators=[DataRequired()])

class TeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired(), Length(min=2, max=100)])
    coach = StringField('Coach', validators=[DataRequired(), Length(max=100)])
    captain_id = SelectField('Captain', coerce=int, validators=[DataRequired()])

# Routes
@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def index():
    players = Player.query.all()
    teams = Team.query.all()
    matches = Match.query.all()
    memberships = Membership.query.all()
    return render_template('index.html', players=players, teams=teams, matches=matches, memberships=memberships)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data
            user_type = form.user_type.data
            
            if user_type == 'admin':
                user = Admin.query.filter_by(email=email).first()
            else:
                user = Player.query.filter_by(name=email).first()
                
            if user and user.check_password(password):
                login_user(user)
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email/username or password', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/players')
def players():
    players = Player.query.all()
    return render_template('players.html', players=players)

@app.route('/teams')
def teams():
    teams = Team.query.all()
    players = Player.query.all()
    return render_template('teams.html', teams=teams, players=players)

@app.route('/matches')
def matches():
    matches = Match.query.all()
    return render_template('matches.html', matches=matches)

@app.route('/add_player', methods=['GET', 'POST'])
@login_required
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        try:
            player = Player(
                name=form.name.data,
                age=form.age.data,
                contact=form.contact.data,
                role=form.role.data
            )
            player.set_password('password123')
            
            db.session.add(player)
            db.session.commit()
            flash('Player added successfully!', 'success')
            return redirect(url_for('players'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding player: {str(e)}', 'danger')
    return render_template('add_player.html', form=form)

@app.route('/add_team', methods=['GET', 'POST'])
@login_required
def add_team():
    form = TeamForm()
    form.captain_id.choices = [(p.player_id, p.name) for p in Player.query.all()]
    
    if form.validate_on_submit():
        try:
            team = Team(
                team_name=form.team_name.data,
                coach=form.coach.data,
                captain_id=form.captain_id.data
            )
            db.session.add(team)
            db.session.commit()
            flash('Team added successfully!', 'success')
            return redirect(url_for('teams'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding team: {str(e)}', 'danger')
    
    return render_template('add_team.html', form=form)

@app.route('/add_match', methods=['GET', 'POST'])
@login_required
def add_match():
    form = MatchForm()
    form.team1.choices = [(t.team_id, t.team_name) for t in Team.query.all()]
    form.team2.choices = form.team1.choices
    
    if form.validate_on_submit():
        try:
            match = Match(
                date=form.date.data,
                location=form.location.data,
                ground=form.ground.data,
                result=form.result.data
            )
            
            team1 = db.session.get(Team, form.team1.data)
            team2 = db.session.get(Team, form.team2.data)
            if team1 and team2:
                match.teams.extend([team1, team2])
            
            db.session.add(match)
            db.session.commit()
            flash('Match added successfully!', 'success')
            return redirect(url_for('matches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding match: {str(e)}', 'danger')
    
    return render_template('add_match.html', form=form)

@app.route('/player/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm(obj=player)
    
    if form.validate_on_submit():
        try:
            player.name = form.name.data
            player.age = form.age.data
            player.contact = form.contact.data
            player.role = form.role.data
            
            db.session.commit()
            flash('Player updated successfully!', 'success')
            return redirect(url_for('players'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating player: {str(e)}', 'danger')
    
    return render_template('edit_player.html', form=form, player=player)

@app.route('/player/<int:player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    try:
        player = Player.query.get_or_404(player_id)
        
        # Check if player is a captain of any team
        teams_with_player_as_captain = Team.query.filter_by(captain_id=player_id).all()
        for team in teams_with_player_as_captain:
            team.captain_id = None
        
        # Delete associated memberships
        Membership.query.filter_by(player_id=player_id).delete()
        
        # Delete associated scorecards
        Scorecard.query.filter_by(player_id=player_id).delete()
        
        # Remove player from teams
        for team in player.teams:
            player.teams.remove(team)
        
        # Delete the player
        db.session.delete(player)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Player deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/match/<int:match_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_match(match_id):
    match = db.session.get(Match, match_id)
    if not match:
        flash('Match not found!', 'danger')
        return redirect(url_for('matches'))
    
    form = MatchForm(obj=match)
    form.team1.choices = [(t.team_id, t.team_name) for t in Team.query.all()]
    form.team2.choices = form.team1.choices
    
    # Set initial team selections
    if match.teams:
        form.team1.data = match.teams[0].team_id
        if len(match.teams) > 1:
            form.team2.data = match.teams[1].team_id
    
    if form.validate_on_submit():
        try:
            match.date = form.date.data
            match.location = form.location.data
            match.ground = form.ground.data
            match.result = form.result.data
            
            # Clear existing teams
            match.teams = []
            
            # Add new teams
            team1 = db.session.get(Team, form.team1.data)
            team2 = db.session.get(Team, form.team2.data)
            if team1 and team2:
                match.teams.extend([team1, team2])
            
            db.session.commit()
            flash('Match updated successfully!', 'success')
            return redirect(url_for('matches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating match: {str(e)}', 'danger')
    
    return render_template('edit_match.html', form=form, match=match)

@app.route('/match/<int:match_id>/delete', methods=['POST'])
@login_required
def delete_match(match_id):
    try:
        match = Match.query.get_or_404(match_id)
        
        # Delete associated scorecards
        Scorecard.query.filter_by(match_id=match_id).delete()
        
        # Clear teams association
        match.teams = []
        
        # Delete the match
        db.session.delete(match)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Match deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        flash('Team not found!', 'danger')
        return redirect(url_for('teams'))
    
    form = TeamForm(obj=team)
    form.captain_id.choices = [(p.player_id, p.name) for p in Player.query.all()]
    
    if form.validate_on_submit():
        try:
            team.team_name = form.team_name.data
            team.coach = form.coach.data
            team.captain_id = form.captain_id.data
            
            db.session.commit()
            flash('Team updated successfully!', 'success')
            return redirect(url_for('teams'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating team: {str(e)}', 'danger')
    
    return render_template('edit_team.html', form=form, team=team)

@app.route('/team/<int:team_id>/players', methods=['GET', 'POST'])
@login_required
def manage_team_players(team_id):
    team = db.session.get(Team, team_id)
    if not team:
        flash('Team not found!', 'danger')
        return redirect(url_for('teams'))
    
    form = FlaskForm()  # Create a basic form for CSRF protection
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            player_id = request.form.get('player_id')
            action = request.form.get('action')
            
            if action == 'add':
                player = db.session.get(Player, player_id)
                if player and player not in team.players:
                    team.players.append(player)
                    flash(f'Added {player.name} to the team!', 'success')
            elif action == 'remove':
                player = db.session.get(Player, player_id)
                if player and player in team.players:
                    team.players.remove(player)
                    flash(f'Removed {player.name} from the team!', 'success')
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error managing team players: {str(e)}', 'danger')
    
    # Get all players and current team players
    all_players = Player.query.all()
    current_players = team.players
    
    return render_template('manage_team_players.html', 
                         team=team, 
                         all_players=all_players, 
                         current_players=current_players,
                         form=form)

@app.route('/team/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        
        # Clear players association
        team.players = []
        
        # Clear matches association
        team.matches = []
        
        # Delete the team
        db.session.delete(team)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Team deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@login_manager.user_loader
def load_user(user_id):
    # Try to load as admin first
    user = db.session.get(Admin, int(user_id))
    if user:
        return user
    # If not admin, try to load as player
    return db.session.get(Player, int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 