import os
from datetime import timedelta

class Config:
    """基本設定クラス"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-key")
    DEBUG = os.environ.get("DEBUG", "True") == "True"
    TESTING = False
    
    # データベース設定
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///numeron.db'
    
    # セッション設定
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # HTTPS環境ではTrueに変更
    
    # アプリケーション設定
    MAX_TURNS = 12
    NUMBER_LENGTH = 3
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/numeron.log'

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///numeron_dev.db'

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Render環境での設定
    LOG_LEVEL = 'WARNING'
    
class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_URL = 'sqlite:///numeron_test.db'

# 設定辞書
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 