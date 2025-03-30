#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import argparse
import re
from datetime import datetime

def is_valid_date(date_str):
    """日付形式（YYYY-MM-DD）が正しいかチェック"""
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not pattern.match(date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def create_transaction(date, template):
    """指定した日付の経費明細を作成"""
    # 日付を設定
    template["ex_transaction"]["recognized_at"] = date
    
    # JSONファイルに保存
    filename = f"transaction_{date}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"Created transaction file for {date}: {filename}")
    
    # APIを使って経費明細を作成
    try:
        result = subprocess.run(
            ["python3", "main.py", "create", filename],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully created transaction for {date}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating transaction for {date}")
        print(e.stderr)
        return False

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='赤坂オフィスへの交通費明細を作成')
    parser.add_argument('dates', nargs='+', help='明細を作成する日付（YYYY-MM-DD形式）')
    parser.add_argument('--template', default='transaction_template.json', help='テンプレートJSONファイル')
    args = parser.parse_args()
    
    # テンプレートJSONファイルを読み込む
    try:
        with open(args.template, 'r', encoding='utf-8') as f:
            template = json.load(f)
    except FileNotFoundError:
        print(f"エラー: テンプレートファイル '{args.template}' が見つかりません")
        return
    except json.JSONDecodeError:
        print(f"エラー: テンプレートファイル '{args.template}' の形式が正しくありません")
        return
    
    # 各日付について経費明細を作成
    success_count = 0
    error_count = 0
    
    for date in args.dates:
        if not is_valid_date(date):
            print(f"エラー: '{date}' は正しい日付形式（YYYY-MM-DD）ではありません")
            error_count += 1
            continue
        
        if create_transaction(date, template):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n処理完了: {success_count}件成功, {error_count}件エラー")

if __name__ == "__main__":
    main()