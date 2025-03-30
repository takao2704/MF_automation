import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# MoneyForward Expense API設定
MF_CLIENT_ID = os.getenv('MF_CLIENT_ID')
MF_CLIENT_SECRET = os.getenv('MF_CLIENT_SECRET')
MF_REDIRECT_URI = os.getenv('MF_REDIRECT_URI', 'https://expense.moneyforward.com/api/oauth2-redirect.html')

# APIのベースURL
MF_API_BASE_URL = 'https://expense.moneyforward.com/api/external/v1'

# オフィスID
MF_OFFICE_ID = os.getenv('MF_OFFICE_ID')

# トークン保存先
TOKEN_FILE = 'token.json'