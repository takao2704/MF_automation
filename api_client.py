import json
import requests
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from auth import MFAuth
from config import MF_API_BASE_URL, MF_OFFICE_ID

class MFExpenseClient:
    """MoneyForward Expense APIクライアント"""
    
    def __init__(self, auth=None):
        """
        初期化
        
        Args:
            auth: MFAuthインスタンス。指定しない場合は新規作成
        """
        self.auth = auth if auth else MFAuth()
        self.session = self.auth.get_session()
        self.base_url = MF_API_BASE_URL
        self.office_id = MF_OFFICE_ID
    
    def _request(self, method, endpoint, params=None, data=None, json_data=None, retry_count=0):
        """
        APIリクエストを送信（改善版）
        
        Args:
            method: HTTPメソッド
            endpoint: エンドポイント
            params: URLパラメータ
            data: リクエストボディ（フォームデータ）
            json_data: リクエストボディ（JSON）
            retry_count: リトライ回数
            
        Returns:
            レスポンスのJSONデータ
        """
        if not self.session:
            raise Exception("認証されていません。先に認証を行ってください。")
            
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
            
        except TokenExpiredError as e:
            # TokenExpiredErrorを明示的にキャッチ
            print(f"トークンの有効期限が切れています。リフレッシュを試行します...")
            if retry_count < 1:  # 1回だけリトライ
                if self.auth.refresh_token():
                    print("トークンのリフレッシュが成功しました。")
                    self.session = self.auth.get_session()
                    return self._request(method, endpoint, params, data, json_data, retry_count + 1)
                else:
                    print("トークンのリフレッシュに失敗しました。再認証が必要です。")
                    raise Exception("トークンのリフレッシュに失敗しました。再認証を行ってください。")
            else:
                print("リトライ回数を超過しました。")
                raise Exception("トークンエラーのリトライ回数を超過しました。")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # 401エラーの場合もトークンリフレッシュを試行
                print(f"401エラーが発生しました。トークンリフレッシュを試行します...")
                if retry_count < 1:  # 1回だけリトライ
                    if self.auth.refresh_token():
                        print("トークンのリフレッシュが成功しました。")
                        self.session = self.auth.get_session()
                        return self._request(method, endpoint, params, data, json_data, retry_count + 1)
                    else:
                        print("トークンのリフレッシュに失敗しました。")
            
            print(f"APIエラー: {e}")
            print(f"レスポンス: {e.response.text}")
            raise
            
        except Exception as e:
            print(f"予期しないエラーが発生しました: {e}")
            raise
    
    def get_offices(self):
        """
        事業者一覧を取得
        
        Returns:
            事業者一覧
        """
        return self._request("GET", "/offices")
    
    def get_ex_transactions(self, office_id=None, page=1, per_page=20, query=None):
        """
        経費明細一覧を取得
        
        Args:
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            page: ページ番号
            per_page: 1ページあたりの件数
            query: 検索クエリ
            
        Returns:
            経費明細一覧
        """
        office_id = office_id or self.office_id
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if query:
            params.update(query)
            
        return self._request("GET", f"/offices/{office_id}/me/ex_transactions", params=params)
    
    def get_ex_transaction(self, transaction_id, office_id=None):
        """
        経費明細の詳細を取得
        
        Args:
            transaction_id: 経費明細ID
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            経費明細の詳細
        """
        office_id = office_id or self.office_id
        return self._request("GET", f"/offices/{office_id}/me/ex_transactions/{transaction_id}")
    
    def create_ex_transaction(self, transaction_data, office_id=None):
        """
        経費明細を作成
        
        Args:
            transaction_data: 経費明細データ
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            作成された経費明細
        """
        office_id = office_id or self.office_id
        return self._request("POST", f"/offices/{office_id}/me/ex_transactions", json_data=transaction_data)
    
    def update_ex_transaction(self, transaction_id, transaction_data, office_id=None):
        """
        経費明細を更新
        
        Args:
            transaction_id: 経費明細ID
            transaction_data: 経費明細データ
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            更新された経費明細
        """
        office_id = office_id or self.office_id
        return self._request("PUT", f"/offices/{office_id}/me/ex_transactions/{transaction_id}", json_data=transaction_data)
    
    def delete_ex_transaction(self, transaction_id, office_id=None):
        """
        経費明細を削除
        
        Args:
            transaction_id: 経費明細ID
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            削除結果
        """
        office_id = office_id or self.office_id
        return self._request("DELETE", f"/offices/{office_id}/me/ex_transactions/{transaction_id}")
    
    def get_ex_reports(self, office_id=None, page=1, per_page=20, query=None):
        """
        経費申請一覧を取得
        
        Args:
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            page: ページ番号
            per_page: 1ページあたりの件数
            query: 検索クエリ
            
        Returns:
            経費申請一覧
        """
        office_id = office_id or self.office_id
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if query:
            params.update(query)
            
        return self._request("GET", f"/offices/{office_id}/me/ex_reports", params=params)
    
    def get_ex_report(self, report_id, office_id=None):
        """
        経費申請の詳細を取得
        
        Args:
            report_id: 経費申請ID
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            経費申請の詳細
        """
        office_id = office_id or self.office_id
        return self._request("GET", f"/offices/{office_id}/me/ex_reports/{report_id}")
    
    def create_ex_report(self, report_data, office_id=None):
        """
        経費申請を作成
        
        Args:
            report_data: 経費申請データ
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            作成された経費申請
        """
        office_id = office_id or self.office_id
        return self._request("POST", f"/offices/{office_id}/me/ex_reports", json_data=report_data)
    
    def update_ex_report(self, report_id, report_data, office_id=None):
        """
        経費申請を更新
        
        Args:
            report_id: 経費申請ID
            report_data: 経費申請データ
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            更新された経費申請
        """
        office_id = office_id or self.office_id
        return self._request("PUT", f"/offices/{office_id}/me/ex_reports/{report_id}", json_data=report_data)
    
    def delete_ex_report(self, report_id, office_id=None):
        """
        経費申請を削除
        
        Args:
            report_id: 経費申請ID
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            削除結果
        """
        office_id = office_id or self.office_id
        return self._request("DELETE", f"/offices/{office_id}/me/ex_reports/{report_id}")
    
    def get_ex_report_types(self, office_id=None):
        """
        経費申請タイプ一覧を取得
        
        Args:
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            経費申請タイプ一覧
        """
        office_id = office_id or self.office_id
        return self._request("GET", f"/offices/{office_id}/ex_report_types")
    
    def create_ex_transaction_for_member(self, office_member_id, transaction_data, office_id=None):
        """
        特定のメンバーに対して経費明細を作成
        
        Args:
            office_member_id: オフィスメンバーID
            transaction_data: 経費明細データ
            office_id: 事業者ID（指定しない場合は設定ファイルの値を使用）
            
        Returns:
            作成された経費明細
        """
        office_id = office_id or self.office_id
        return self._request("POST", f"/offices/{office_id}/office_members/{office_member_id}/ex_transactions", json_data=transaction_data)