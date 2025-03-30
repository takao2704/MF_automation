#!/usr/bin/env python3
import argparse
import json
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs

from auth import MFAuth
from api_client import MFExpenseClient
from config import MF_OFFICE_ID

def authenticate():
    """認証処理を行う"""
    auth = MFAuth()
    
    # すでに認証済みの場合はセッションを返す
    if auth.get_session():
        print("既存のトークンを使用します")
        return auth
    
    # 認証URLを取得してブラウザで開く
    auth_url, state = auth.get_authorization_url()
    print(f"ブラウザで認証を行います: {auth_url}")
    webbrowser.open(auth_url)
    
    # コールバックURLに応じて入力を求める
    if auth.redirect_uri == 'urn:ietf:wg:oauth:2.0:oob':
        # 認証コードを直接入力してもらう
        print("\nブラウザで認証後、表示された認証コードを入力してください:")
        auth_code = input("> ")
        
        # トークンを取得
        auth.fetch_token(auth_code)
    else:
        # リダイレクトされたURLを入力してもらう
        print("\nブラウザで認証後、リダイレクトされたURLを入力してください:")
        redirect_url = input("> ")
        
        # トークンを取得
        auth.fetch_token(redirect_url)
    
    print("認証が完了しました")
    return auth

def list_offices(client):
    """事業者一覧を表示"""
    offices = client.get_offices()
    print(json.dumps(offices, indent=2, ensure_ascii=False))
    return offices

def list_transactions(client, args):
    """経費明細一覧を表示"""
    query = {}
    if args.unsubmitted:
        query['is_unsubmitted'] = 'true'
    if args.sort:
        query['sort'] = args.sort
    
    transactions = client.get_ex_transactions(
        page=args.page,
        per_page=args.per_page,
        query=query
    )
    print(json.dumps(transactions, indent=2, ensure_ascii=False))
    return transactions

def get_transaction(client, args):
    """経費明細の詳細を表示"""
    transaction = client.get_ex_transaction(args.id)
    print(json.dumps(transaction, indent=2, ensure_ascii=False))
    return transaction

def create_transaction(client, args):
    """経費明細を作成"""
    # JSONファイルから経費明細データを読み込む
    with open(args.json_file, 'r', encoding='utf-8') as f:
        transaction_data = json.load(f)
    
    result = client.create_ex_transaction(transaction_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def create_transaction_for_member(client, args):
    """特定のメンバーに対して経費明細を作成"""
    # JSONファイルから経費明細データを読み込む
    with open(args.json_file, 'r', encoding='utf-8') as f:
        transaction_data = json.load(f)
    
    result = client.create_ex_transaction_for_member(args.member_id, transaction_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def update_transaction(client, args):
    """経費明細を更新"""
    # JSONファイルから経費明細データを読み込む
    with open(args.json_file, 'r', encoding='utf-8') as f:
        transaction_data = json.load(f)
    
    result = client.update_ex_transaction(args.id, transaction_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def delete_transaction(client, args):
    """経費明細を削除"""
    result = client.delete_ex_transaction(args.id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def list_reports(client, args):
    """経費申請一覧を表示"""
    reports = client.get_ex_reports(
        page=args.page,
        per_page=args.per_page
    )
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    return reports

def list_report_types(client):
    """経費申請タイプ一覧を表示"""
    report_types = client.get_ex_report_types()
    print(json.dumps(report_types, indent=2, ensure_ascii=False))
    return report_types

def get_report(client, args):
    """経費申請の詳細を表示"""
    report = client.get_ex_report(args.id)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report

def create_report(client, args):
    """経費申請を作成"""
    # JSONファイルから経費申請データを読み込む
    with open(args.json_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    result = client.create_ex_report(report_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def update_report(client, args):
    """経費申請を更新"""
    # JSONファイルから経費申請データを読み込む
    with open(args.json_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    result = client.update_ex_report(args.id, report_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def delete_report(client, args):
    """経費申請を削除"""
    result = client.delete_ex_report(args.id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result

def create_example_json():
    """経費明細作成用のサンプルJSONファイルを作成"""
    example_data = {
        "ex_transaction": {
            "office_member_id": "OFFICE_MEMBER_ID",
            "transaction_date": "2023-01-01",
            "amount": 1000,
            "reason": "サンプル経費",
            "ex_item_id": "EX_ITEM_ID",
            "dept_id": "DEPT_ID"
        }
    }
    
    with open('example_transaction.json', 'w', encoding='utf-8') as f:
        json.dump(example_data, f, indent=2, ensure_ascii=False)
    
    print("サンプルJSONファイルを作成しました: example_transaction.json")

def create_report_example_json():
    """経費申請作成用のサンプルJSONファイルを作成"""
    example_data = {
        "ex_report": {
            "title": "2024年12月交通費",
            "ex_report_type_id": "EX_REPORT_TYPE_ID"
        }
    }
    
    with open('example_report.json', 'w', encoding='utf-8') as f:
        json.dump(example_data, f, indent=2, ensure_ascii=False)
    
    print("経費申請用サンプルJSONファイルを作成しました: example_report.json")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='MoneyForward Expense API CLI')
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # 認証コマンド
    auth_parser = subparsers.add_parser('auth', help='認証を行う')
    
    # 事業者一覧コマンド
    offices_parser = subparsers.add_parser('offices', help='事業者一覧を取得')
    
    # 経費明細一覧コマンド
    list_parser = subparsers.add_parser('list', help='経費明細一覧を取得')
    list_parser.add_argument('--page', type=int, default=1, help='ページ番号')
    list_parser.add_argument('--per-page', type=int, default=20, help='1ページあたりの件数')
    list_parser.add_argument('--unsubmitted', action='store_true', help='未申請の経費明細のみを表示')
    list_parser.add_argument('--sort', help='ソート条件（例: created_at.desc）')
    
    # 経費明細詳細コマンド
    get_parser = subparsers.add_parser('get', help='経費明細の詳細を取得')
    get_parser.add_argument('id', help='経費明細ID')
    
    # 経費明細作成コマンド
    create_parser = subparsers.add_parser('create', help='経費明細を作成')
    create_parser.add_argument('json_file', help='経費明細データのJSONファイル')
    
    # 特定のメンバーに対して経費明細作成コマンド
    create_member_parser = subparsers.add_parser('create-for-member', help='特定のメンバーに対して経費明細を作成')
    create_member_parser.add_argument('member_id', help='オフィスメンバーID')
    create_member_parser.add_argument('json_file', help='経費明細データのJSONファイル')
    
    # 経費明細更新コマンド
    update_parser = subparsers.add_parser('update', help='経費明細を更新')
    update_parser.add_argument('id', help='経費明細ID')
    update_parser.add_argument('json_file', help='経費明細データのJSONファイル')
    
    # 経費明細削除コマンド
    delete_parser = subparsers.add_parser('delete', help='経費明細を削除')
    delete_parser.add_argument('id', help='経費明細ID')
    
    # サンプルJSONファイル作成コマンド
    example_parser = subparsers.add_parser('example', help='経費明細用サンプルJSONファイルを作成')
    
    # 経費申請一覧コマンド
    report_list_parser = subparsers.add_parser('report-list', help='経費申請一覧を取得')
    report_list_parser.add_argument('--page', type=int, default=1, help='ページ番号')
    report_list_parser.add_argument('--per-page', type=int, default=20, help='1ページあたりの件数')
    
    # 経費申請詳細コマンド
    report_get_parser = subparsers.add_parser('report-get', help='経費申請の詳細を取得')
    report_get_parser.add_argument('id', help='経費申請ID')
    
    # 経費申請作成コマンド
    report_create_parser = subparsers.add_parser('report-create', help='経費申請を作成')
    report_create_parser.add_argument('json_file', help='経費申請データのJSONファイル')
    
    # 経費申請更新コマンド
    report_update_parser = subparsers.add_parser('report-update', help='経費申請を更新')
    report_update_parser.add_argument('id', help='経費申請ID')
    report_update_parser.add_argument('json_file', help='経費申請データのJSONファイル')
    
    # 経費申請削除コマンド
    report_delete_parser = subparsers.add_parser('report-delete', help='経費申請を削除')
    report_delete_parser.add_argument('id', help='経費申請ID')
    
    # 経費申請タイプ一覧コマンド
    report_types_parser = subparsers.add_parser('report-types', help='経費申請タイプ一覧を取得')
    
    # 経費申請用サンプルJSONファイル作成コマンド
    report_example_parser = subparsers.add_parser('report-example', help='経費申請用サンプルJSONファイルを作成')
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return
    
    # サンプルJSONファイル作成コマンドの場合は認証不要
    if args.command == 'example':
        create_example_json()
        return
    elif args.command == 'report-example':
        create_report_example_json()
        return
    
    # 認証処理
    auth = authenticate()
    client = MFExpenseClient(auth)
    
    # コマンドに応じた処理を実行
    if args.command == 'auth':
        print("認証が完了しています")
    elif args.command == 'offices':
        list_offices(client)
    elif args.command == 'list':
        list_transactions(client, args)
    elif args.command == 'get':
        get_transaction(client, args)
    elif args.command == 'create':
        create_transaction(client, args)
    elif args.command == 'create-for-member':
        create_transaction_for_member(client, args)
    elif args.command == 'update':
        update_transaction(client, args)
    elif args.command == 'delete':
        delete_transaction(client, args)
    elif args.command == 'report-list':
        list_reports(client, args)
    elif args.command == 'report-get':
        get_report(client, args)
    elif args.command == 'report-create':
        create_report(client, args)
    elif args.command == 'report-update':
        update_report(client, args)
    elif args.command == 'report-delete':
        delete_report(client, args)
    elif args.command == 'report-types':
        list_report_types(client)

if __name__ == '__main__':
    main()