from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from models import (
    BgmiScore,
    CodScore,
    Game,
    LeaderboardEntry,
    PubgScore,
    User,
    ValorantScore,
    db,
)


api = Blueprint("api", __name__)

# Map game names to their dedicated score tables.
SCORE_MODELS = {
    "pubg": PubgScore,
    "cod": CodScore,
    "bgmi": BgmiScore,
    "valorant": ValorantScore,
}


def get_game_by_name(game_name: str) -> Game | None:
    normalized = game_name.strip().lower()
    if not normalized:
        return None
    return Game.query.filter(func.lower(Game.name) == normalized).first()


def success(message: str, data=None, status: int = 200):
    # Standard success envelope for all API responses.
    return jsonify({"success": True, "message": message, "data": data}), status


def error(message: str, status: int = 400):
    # Standard error envelope for all API responses.
    return jsonify({"success": False, "message": message}), status


def build_leaderboard(game: Game, limit: int | None) -> dict:
    query = (
        LeaderboardEntry.query.filter_by(game_id=game.id)
        .order_by(LeaderboardEntry.highest_score.desc(), LeaderboardEntry.saved_at.desc())
    )
    if limit:
        query = query.limit(limit)

    entries = query.all()
    leaderboard = []
    for index, entry in enumerate(entries, start=1):
        leaderboard.append(
            {
                "rank": index,
                "player_id": entry.user_id,
                "display_name": entry.user.display_name,
                "highest_score": entry.highest_score,
                "saved_at": entry.saved_at.isoformat(),
            }
        )

    return {"game": game.to_dict(), "leaderboard": leaderboard}


def build_global_leaderboard(limit: int | None) -> list[dict]:
    # Join leaderboard entries with users and games for a single global list.
    query = (
        db.session.query(LeaderboardEntry, User, Game)
        .join(User, LeaderboardEntry.user_id == User.id)
        .join(Game, LeaderboardEntry.game_id == Game.id)
        .order_by(LeaderboardEntry.highest_score.desc(), LeaderboardEntry.saved_at.desc())
    )
    if limit:
        query = query.limit(limit)

    rows = query.all()
    leaderboard = []
    for index, (entry, user, game) in enumerate(rows, start=1):
        leaderboard.append(
            {
                "rank": index,
                "player_id": user.id,
                "display_name": user.display_name,
                "game_name": game.name,
                "highest_score": entry.highest_score,
                "saved_at": entry.saved_at.date().isoformat(),
            }
        )

    return leaderboard


@api.post("/users")
def create_user():
    payload = request.get_json(silent=True) or {}
    display_name = (payload.get("display_name") or "").strip()

    if not display_name:
        return error("display_name is required", 400)

    user = User(display_name=display_name)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error("unable to create user", 500)

    return success("User created successfully", user.to_dict(), 201)


@api.post("/games")
def create_game():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()

    if not name:
        return error("name is required", 400)

    if Game.query.filter(func.lower(Game.name) == name.lower()).first():
        return error("game already exists", 409)

    game = Game(name=name)
    db.session.add(game)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error("unable to create game", 500)

    return success("Game created successfully", game.to_dict(), 201)


@api.post("/scores/<string:game_name>")
def submit_score(game_name: str):
    # Accept a score from a game server and keep only the highest per user.
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    score = payload.get("score")

    score_model = SCORE_MODELS.get(game_name.lower())
    if score_model is None:
        return error("game not found", 404)

    if user_id is None or score is None:
        return error("invalid or missing score", 400)

    try:
        score = int(score)
    except (TypeError, ValueError):
        return error("invalid or missing score", 400)

    if score < 0:
        return error("negative score submission", 400)

    user = db.session.get(User, user_id)
    if user is None:
        return error("user not found", 404)

    game = get_game_by_name(game_name)
    if game is None:
        return error("game not found", 404)

    # Keep only the highest score per user in the per-game table.
    existing_score = (
        score_model.query.filter_by(user_id=user.id)
        .order_by(score_model.score.desc())
        .first()
    )
    if existing_score is None:
        existing_score = score_model(user_id=user.id, score=score)
        db.session.add(existing_score)
    elif score > existing_score.score:
        existing_score.score = score
        existing_score.created_at = datetime.utcnow()

    if existing_score is not None:
        score_model.query.filter(
            score_model.user_id == user.id, score_model.id != existing_score.id
        ).delete(synchronize_session=False)

    entry = LeaderboardEntry.query.filter_by(user_id=user.id, game_id=game.id).first()
    if entry is None:
        entry = LeaderboardEntry(
            user_id=user.id,
            game_id=game.id,
            highest_score=score,
            saved_at=datetime.utcnow(),
        )
        db.session.add(entry)
    elif score > entry.highest_score:
        # Only update the leaderboard if this score beats the previous best.
        entry.highest_score = score
        entry.saved_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error("unable to submit score", 500)

    response = entry.to_dict()
    response.update({"display_name": user.display_name, "game": game.name})
    return success("Score submitted successfully", response, 201)


@api.get("/leaderboard/<string:game_name>")
def leaderboard_by_game(game_name: str):
    game = get_game_by_name(game_name)
    if game is None:
        return error("game not found", 404)

    limit = request.args.get("limit", type=int)
    return success("Leaderboard fetched successfully", build_leaderboard(game, limit))


@api.get("/leaderboard")
def leaderboard_global():
    # Global leaderboard across all games.
    limit = request.args.get("limit", type=int)
    return success("Leaderboard fetched successfully", build_global_leaderboard(limit))


@api.get("/leaderboard/<string:game_name>/top")
def leaderboard_top(game_name: str):
    limit = request.args.get("limit", type=int) or 10
    game = get_game_by_name(game_name)
    if game is None:
        return error("game not found", 404)
    return success("Leaderboard fetched successfully", build_leaderboard(game, limit))
