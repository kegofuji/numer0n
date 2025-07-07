from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class Game(db.Model):
    """ゲーム履歴モデル"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    winner = db.Column(db.String(10))  # 'player1', 'player2', 'draw'
    total_turns = db.Column(db.Integer)
    player1_number = db.Column(db.String(3))
    player2_number = db.Column(db.String(3))
    
    # リレーション
    moves = db.relationship('GameMove', backref='game', lazy=True, cascade='all, delete-orphan')
    
    @hybrid_property
    def duration(self):
        """ゲーム時間を計算"""
        if self.finished_at:
            return self.finished_at - self.created_at
        return datetime.utcnow() - self.created_at

class GameMove(db.Model):
    """ゲームの手番履歴モデル"""
    __tablename__ = 'game_moves'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    turn = db.Column(db.Integer, nullable=False)
    player = db.Column(db.Integer, nullable=False)  # 1 or 2
    guess = db.Column(db.String(3), nullable=False)
    eat = db.Column(db.Integer, nullable=False)
    bite = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlayerStats(db.Model):
    """プレイヤー統計モデル"""
    __tablename__ = 'player_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(50), unique=True, nullable=False)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    total_turns = db.Column(db.Integer, default=0)
    average_turns = db.Column(db.Float, default=0.0)
    best_score = db.Column(db.Integer)  # 最短ターン数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @hybrid_property
    def win_rate(self):
        """勝率を計算"""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100 