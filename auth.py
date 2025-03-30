import json
import os
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from config import MF_CLIENT_ID, MF_CLIENT_SECRET, MF_REDIRECT_URI, TOKEN_FILE

class MFAuth:
    """MoneyForward Expense API認証クラス"""
    
    def __init__(self):
        self.client_id = MF_CLIENT_ID
        self.client_secret = MF_CLIENT_SECRET
        self.redirect_uri = MF_REDIRECT_URI
        self.token = None
        self.oauth = None
        
        # 保存されたトークンがあれば読み込む
        self._load_token()
    
    def _load_token(self):
        """保存されたトークンを読み込む"""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                self.token = json.load(f)
                self.oauth = OAuth2Session(
                    client_id=self.client_id,
                    token=self.token
                )
            return True
        return False
    
    def _save_token(self):
        """トークンを保存する"""
        with open(TOKEN_FILE, 'w') as f:
            json.dump(self.token, f)
    
    def get_authorization_url(self):
        """認証URLを取得する"""
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=['office_setting:write', 'user_setting:write', 'transaction:write',
                   'report:write', 'account:write', 'public_resource:read']
        )
        authorization_url, state = oauth.authorization_url(
            'https://expense.moneyforward.com/oauth/authorize'
        )
        return authorization_url, state
    
    def fetch_token(self, authorization_response_or_code):
        """認証コードからトークンを取得する
        
        Args:
            authorization_response_or_code: 認証レスポンスのURLまたは認証コード
        """
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri
        )
        
        # urn:ietf:wg:oauth:2.0:oob の場合は認証コードを直接使用
        if self.redirect_uri == 'urn:ietf:wg:oauth:2.0:oob' and not authorization_response_or_code.startswith('http'):
            self.token = oauth.fetch_token(
                'https://expense.moneyforward.com/oauth/token',
                code=authorization_response_or_code,
                client_secret=self.client_secret
            )
        else:
            # 通常のリダイレクトURLの場合
            self.token = oauth.fetch_token(
                'https://expense.moneyforward.com/oauth/token',
                authorization_response=authorization_response_or_code,
                client_secret=self.client_secret
            )
            
        self.oauth = oauth
        self._save_token()
        return self.token
    
    def refresh_token(self):
        """トークンをリフレッシュする"""
        if not self.token:
            return False
            
        extra = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        self.oauth = OAuth2Session(
            client_id=self.client_id,
            token=self.token
        )
        
        self.token = self.oauth.refresh_token(
            'https://expense.moneyforward.com/oauth/token',
            **extra
        )
        self._save_token()
        return True
    
    def get_session(self):
        """認証済みのセッションを取得する"""
        if not self.oauth:
            return None
        return self.oauth