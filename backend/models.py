from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



# USER MODEL
# Stores all users/players
class User(db.Model):
    __tablename__ = "users"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Player display name
    display_name = db.Column(db.String(120), nullable=False)

    # Timestamp when user is created
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One user can have many leaderboard entries.
    leaderboard_entries = db.relationship(
        "LeaderboardEntry",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship with PUBG scores table
    pubg_scores = db.relationship(
        "PubgScore",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Relationship with COD scores table
    cod_scores = db.relationship(
        "CodScore",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Relationship with BGMI scores table
    bgmi_scores = db.relationship(
        "BgmiScore",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Relationship with Valorant scores table
    valorant_scores = db.relationship(
        "ValorantScore",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Convert model object to dictionary
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
        }

# GAME MODEL
# Stores all games
class Game(db.Model):
    __tablename__ = "games"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Game name
    # unique=True prevents duplicate game names
    name = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship with leaderboard entries
    # One game can have many leaderboard entries
    leaderboard_entries = db.relationship(
        "LeaderboardEntry",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    # Convert object to dictionary
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }

# MAIN LEADERBOARD MODEL
# Stores highest score of each user for each game
class LeaderboardEntry(db.Model):
    __tablename__ = "leaderboard_entries"

    # Table constraints and indexes
    __table_args__ = (

        # Prevent duplicate leaderboard rows
        # One user can only have one entry per game
        db.UniqueConstraint(
            "user_id",
            "game_id",
            name="uq_user_game"
        ),

        # Useful for sorting by score
        db.Index(
            "ix_game_score",
            "game_id",
            "highest_score"
        ),
    )

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking to users table
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Foreign key linking to games table
    game_id = db.Column(
        db.Integer,
        db.ForeignKey("games.id"),
        nullable=False
    )

    # Stores highest score only
    highest_score = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # Timestamp when leaderboard was updated
    saved_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship with User model
    user = db.relationship(
        "User",
        back_populates="leaderboard_entries"
    )

    # Relationship with Game model
    game = db.relationship(
        "Game",
        back_populates="leaderboard_entries"
    )

    # Convert object to dictionary
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "highest_score": self.highest_score,
            "saved_at": self.saved_at.isoformat(),
        }

# PUBG SCORE TABLE
# Stores raw PUBG scores from game server
class PubgScore(db.Model):
    __tablename__ = "pubg_scores"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking to users table
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Score submitted by user
    score = db.Column(db.Integer, nullable=False)

    # Timestamp when score was submitted
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship with User model
    user = db.relationship(
        "User",
        back_populates="pubg_scores"
    )

# COD SCORE TABLE
class CodScore(db.Model):
    __tablename__ = "cod_scores"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    score = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="cod_scores"
    )

# BGMI SCORE TABLE
class BgmiScore(db.Model):
    __tablename__ = "bgmi_scores"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    score = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="bgmi_scores"
    )

# VALORANT SCORE TABLE
class ValorantScore(db.Model):
    __tablename__ = "valorant_scores"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    score = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="valorant_scores"
    )