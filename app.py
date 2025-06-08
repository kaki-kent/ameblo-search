from flask import Flask, render_template, request, send_from_directory
import requests
from bs4 import BeautifulSoup
import datetime
import os
import urllib.parse # <- 新しく追加

# バージョン情報: ソースを修正するたびに+0.1ずつ加算する
__version__ = "0.4" # バージョンを0.4に更新

app = Flask(__name__)

# ▼▼▼ scrape_ameblo関数を全面的に修正 ▼▼▼
def scrape_ameblo(query):
    """
    Amebaブログの"新しい"サイト内検索結果をスクレイピングする関数
    """
    if not query:
        return []

    # 日本語キーワードをURLエンコードする
    query_encoded = urllib.parse.quote(query)
    
    # 新しいAmebaブログの検索URL形式
    search_url = f"https://search.ameba.jp/search/entry/{query_encoded}.html?aid=kaki-kent"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return [{"title": "ページの取得に失敗しました", "link": "#", "description": str(e)}]

    soup = BeautifulSoup(response.content, 'html.parser')
    
    results = []
    # 新しいHTML構造に対応したセレクタ（目印）に変更
    # [data-testid="..."] という属性を目印にする
    for item in soup.select('[data-testid="result-item"]'):
        title_tag = item.select_one('[data-testid="result-item-title"]')
        description_tag = item.select_one('[data-testid="result-item-snippet"]')
        
        if title_tag and description_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag.get('href')
            description = description_tag.get_text(strip=True)
            results.append({'title': title, 'link': link, 'description': description})
            
    return results
# ▲▲▲ ここまでが修正箇所 ▲▲▲


@app.route('/', methods=['GET', 'POST'])
def search():
    search_query = ""
    results = []
    if request.method == 'POST':
        search_query = request.form['query']
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'search_log.txt')
        with open(log_file_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {search_query}\n")
        results = scrape_ameblo(search_query)
    return render_template('index.html', query=search_query, results=results, version=__version__)


@app.route('/download_log')
def download_log_file():
    log_dir = 'logs'
    log_filename = 'search_log.txt'
    log_path = os.path.join(log_dir, log_filename)
    if not os.path.exists(log_path):
        return "ログファイルはまだ作成されていません。一度、検索を実行してください。", 404
    return send_from_directory(log_dir, log_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
