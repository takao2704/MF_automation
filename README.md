# MoneyForward Expense API 自動化ツール

MoneyForward Expense APIを使用して、経費明細の作成を自動化するツールです。

## セットアップ

1. 必要なパッケージをインストール
   ```
   pip install -r requirements.txt
   ```

2. 環境変数の設定
   `.env.example`をコピーして`.env`ファイルを作成し、必要な情報を設定します。
   ```
   cp .env.example .env
   ```

3. `.env`ファイルを編集して、以下の情報を設定します：
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   REDIRECT_URI=your_redirect_uri
   OFFICE_ID=your_office_id
   ```

## 使い方

### 経費明細の作成

指定した日付の経費明細を作成します。

```
python3 create_transactions.py 2024-12-01 2024-12-02 2024-12-03
```

複数の日付を指定することで、一度に複数の経費明細を作成できます。

### オプション

- `--template`: テンプレートJSONファイルを指定します（デフォルト: `transaction_template.json`）

```
python3 create_transactions.py 2024-12-01 --template custom_template.json
```

## テンプレートファイル

テンプレートファイル（`transaction_template.json`）には、経費明細の基本情報が含まれています。
このファイルを編集することで、作成される経費明細の内容をカスタマイズできます。

```json
{
  "ex_transaction": {
    "recognized_at": "2024-12-01",
    "value": 504,
    "remark": "元赤坂オフィス (平和台(東京都)~赤坂見附 往復電車代)",
    "memo": "平和台(東京都) -> 新宿三丁目 -> 赤坂見附",
    "currency": "JPY",
    "jpyrate": 1.0,
    "use_custom_jpy_rate": false,
    "ex_item_id": "svStdCnC5cVghDib7uJACA",
    "dr_excise_id": "RgCz_0-_NktCGAF3o4xNTA",
    "dept_id": "P8EYuTfTRlCzpmhJxLzciw",
    "cr_item_id": "Ij4fDogDW4xfrBtMupArGQ",
    "cr_sub_item_id": "dhNueknVU8xcK-uyQ3tc4w"
  }
}
```

## 例

### 特定の日付の経費明細を作成

```
python3 create_transactions.py 2024-12-01
```

### 複数の日付の経費明細を作成

```
python3 create_transactions.py 2024-12-01 2024-12-05 2024-12-10 2024-12-15 2024-12-20
```

### 月の最初の営業日（1日、8日、15日、22日、29日）の経費明細を作成

```
python3 create_transactions.py 2024-12-01 2024-12-08 2024-12-15 2024-12-22 2024-12-29