# app.py

# ==============================================================================
# バージョン管理メモ
# ------------------------------------------------------------------------------
# このプログラムのバージョンは、ソースコードを変更するたびに0.1ずつ増やします。
# 例: 0.0 -> 0.1 -> 0.2 ...
# バージョン情報は、検索キーワード入力フォームのタイトル右横に表示されます。
#
# 現在のバージョン: 0.0
# ==============================================================================

from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# AmebaブログのIDを設定してください
AMEBA_BLOG_ID = "kaki-kent" 

# 現在のバージョン
APP_VERSION = "0.0"

@app.route('/', methods=['GET'])
def index():
    """
    検索キーワード入力フォームを表示します。
    """
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ブログ内検索 (Ver{{ version }})</title>
            <style>
                body { font-family: sans-serif; margin: 20px; text-align: center; }
                .container { max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                input[type="text"] { width: calc(100% - 22px); padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }
                input[type="submit"] { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                input[type="submit"]:hover { background-color: #0056b3; }
                footer { margin-top: 30px; font-size: 0.8em; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{{ AMEBA_BLOG_ID }} さんのブログ内検索</h1>
                <form action="/search" method="get">
                    <input type="text" name="keyword" placeholder="検索キーワードを入力" required>
                    <input type="submit" value="検索">
                </form>
            </div>
            <footer>
                <p>このサービスはAmebaブログの検索機能を利用しています。</p>
            </footer>
        </body>
        </html>
    """, version=APP_VERSION, AMEBA_BLOG_ID=AMEBA_BLOG_ID)

@app.route('/search', methods=['GET'])
def search():
    """
    キーワードを受け取り、Amebaブログの検索URLにリダイレクトします。
    """
    keyword = request.args.get('keyword', '')
    
    # URLエンコードはFlaskのredirectが自動的に行ってくれるため、ここでは不要です
    # ただし、特定の文字（例: スペース）はURLエンコードが必要なため、
    # Flaskのredirect関数に任せるのが最も確実です。
    search_url = f"https://search.ameba.jp/search/entry/{keyword}.html?&sortField=0&p=1&aid={AMEBA_BLOG_ID}"
    
    return redirect(search_url)

if __name__ == '__main__':
    app.run(debug=True)
