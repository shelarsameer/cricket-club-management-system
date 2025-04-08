from app import db, Player, Team, Match, Admin, Membership, Scorecard, app
from datetime import datetime, timedelta, date
import random

def add_dummy_data():
    # Clear existing data
    db.session.query(Scorecard).delete()
    db.session.query(Membership).delete()
    db.session.query(Match).delete()
    db.session.query(Team).delete()
    db.session.query(Player).delete()
    db.session.query(Admin).delete()
    db.session.commit()
    
    print("Adding dummy data...")
    
    # Add admin
    admin = Admin(
        name="John Smith",
        contact="1234567890",
        email="admin@cricketclub.com"
    )
    admin.set_password("password123")
    db.session.add(admin)
    db.session.commit()
    print("Added admin")
    
    # Add players
    players = []
    player_roles = ["Batsman", "Bowler", "All-Rounder", "Wicket Keeper"]
    player_names = [
        "Virat Kohli", "Steve Smith", "Kane Williamson", "Joe Root", 
        "Ben Stokes", "Pat Cummins", "Jasprit Bumrah", "Rohit Sharma",
        "David Warner", "Jos Buttler", "Ravindra Jadeja", "Rashid Khan"
    ]
    
    for i, name in enumerate(player_names):
        player = Player(
            name=name,
            age=random.randint(20, 35),
            contact=f"+91{random.randint(7000000000, 9999999999)}",
            role=random.choice(player_roles)
        )
        player.set_password("password123")
        db.session.add(player)
        players.append(player)
    
    db.session.commit()
    print(f"Added {len(players)} players")
    
    # Add teams
    teams = []
    team_names = ["Red Dragons", "Blue Eagles", "Green Lions", "Yellow Tigers"]
    
    for team_name in team_names:
        # Randomly select a captain from players
        captain = random.choice(players)
        
        team = Team(
            team_name=team_name,
            coach=f"Coach {random.choice(['Anderson', 'Johnson', 'Williams', 'Brown'])}",
            captain_id=captain.player_id
        )
        db.session.add(team)
        teams.append(team)
    
    db.session.commit()
    print(f"Added {len(teams)} teams")
    
    # Assign players to teams
    for team in teams:
        # Randomly assign 5-8 players to each team
        team_players = random.sample(players, random.randint(5, 8))
        for player in team_players:
            team.players.append(player)
    
    db.session.commit()
    print("Assigned players to teams")
    
    # Add memberships
    membership_types = ["Annual", "Monthly", "Quarterly"]
    today = date.today()
    
    for player in players:
        # 70% chance of having a membership
        if random.random() < 0.7:
            membership_type = random.choice(membership_types)
            
            # Set join date to a random date in the past 6 months
            join_date = today - timedelta(days=random.randint(0, 180))
            
            # Set expiry date based on membership type
            if membership_type == "Annual":
                expiry_date = join_date + timedelta(days=365)
            elif membership_type == "Monthly":
                expiry_date = join_date + timedelta(days=30)
            else:  # Quarterly
                expiry_date = join_date + timedelta(days=90)
            
            membership = Membership(
                player_id=player.player_id,
                join_date=join_date,
                expiry_date=expiry_date,
                membership_type=membership_type,
                admin_id=admin.admin_id
            )
            db.session.add(membership)
    
    db.session.commit()
    print("Added memberships")
    
    # Add matches
    matches = []
    locations = ["Main Ground", "City Stadium", "Community Field", "Sports Complex"]
    grounds = ["Pitch 1", "Pitch 2", "Pitch 3", "Pitch 4"]
    results = ["Team 1 Won", "Team 2 Won", "Draw", None]  # None for upcoming matches
    
    # Generate matches for the next 30 days
    for i in range(10):
        # Random date in the next 30 days
        match_date = today + timedelta(days=random.randint(1, 30))
        
        # Randomly select two different teams
        match_teams = random.sample(teams, 2)
        
        match = Match(
            date=match_date,
            location=random.choice(locations),
            ground=random.choice(grounds),
            result=random.choice(results) if match_date < today else None
        )
        db.session.add(match)
        matches.append(match)
        
        # Add teams to match
        for team in match_teams:
            match.teams.append(team)
    
    db.session.commit()
    print(f"Added {len(matches)} matches")
    
    # Add scorecards for past matches
    for match in matches:
        if match.date < today and match.result:
            # Get players from both teams
            match_players = []
            for team in match.teams:
                match_players.extend(team.players)
            
            # Add scorecards for 5-10 players
            for player in random.sample(match_players, min(random.randint(5, 10), len(match_players))):
                scorecard = Scorecard(
                    match_id=match.match_id,
                    player_id=player.player_id,
                    runs=random.randint(0, 150),
                    wickets=random.randint(0, 5)
                )
                db.session.add(scorecard)
    
    db.session.commit()
    print("Added scorecards")
    
    print("Dummy data added successfully!")

if __name__ == "__main__":
    with app.app_context():
        add_dummy_data() 