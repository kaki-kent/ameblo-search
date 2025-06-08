from flask import Flask, render_template, request, send_from_directory, redirect
import urllib.parse
import datetime
import os

# バージョン情報: 最終版
__version__ = "0.8"

app = Flask(__name__)

# トップページを表示するための関数
@app.route('/')
def index():
    return render_template('index.html', version=__version__)

# 検索キーワードを受け取ってログを記録し、Amebaへリダイレクトさせるための関数
@app.route('/search', methods=['POST'])
def search_and_redirect():
    # フォームから検索キーワードを取得
    search_query = request.form.get('query', '')

    # キーワードが空でなければ、ログを記録する
    if search_query:
        # --- ログ記録のコード ---
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'search_log.txt')
        with open(log_file_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {search_query}\n")
        # --- ログ記録ここまで ---

        # Amebaの検索URLを組み立てる
        query_encoded = urllib.parse.quote(search_query)
        ameba_url = f"https://search.ameba.jp/search/entry/{query_encoded}.html?aid=kaki-kent"
        
        # 組み立てたAmebaのURLにリダイレクト（ジャンプ）させる
        return redirect(ameba_url)
    
    # キーワードが空の場合は、トップページに戻す
    return redirect('/')

# ログダウンロード機能はそのまま残す
@app.route('/download_log')
def download_log_file():
    log_dir = 'logs'
    log_filename = 'search_log.txt'
    log_path = os.path.join(log_dir, log_filename)
    if not os.path.exists(log_path):
        return "ログファイルはまだ作成されていません。", 404
    return send_from_directory(log_dir, log_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
