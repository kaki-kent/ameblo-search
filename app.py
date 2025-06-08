from flask import Flask, render_template, request, send_from_directory
import requests
from bs4 import BeautifulSoup
import datetime
import os
import urllib.parse
import json # <- 新しく追加

# バージョン情報: ソースを修正するたびに+0.1ずつ加算する
__version__ = "0.5" # バージョンを0.5に更新

app = Flask(__name__)

# ▼▼▼ scrape_ameblo関数を「宝の地図」作戦に書き換え ▼▼▼
def scrape_ameblo(query):
    if not query:
        return []

    query_encoded = urllib.parse.quote(query)
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
    
    # 「宝の地図」である __NEXT_DATA__ というscriptタグを探す
    next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
    
    if not next_data_script:
        print("Error: Could not find the result data (__NEXT_DATA__).")
        return []

    try:
        # 地図（JSON文字列）を読み解いて、Pythonのデータに変換
        data = json.loads(next_data_script.string)
        # 地図の中から記事一覧（entries）の場所を探す
        entries = data['props']['pageProps']['searchResult']['entries']
    except (json.JSONDecodeError, KeyError, TypeError):
        # 地図が読み解けない、または記事一覧がない場合は0件とする
        print("Error: Failed to parse JSON or find entries.")
        return []

    results = []
    for entry in entries:
        # titleやcontentには<mark>タグなどが含まれるため、再度パースして文字だけ抽出
        title_soup = BeautifulSoup(entry.get('title', ''), 'html.parser')
        description_soup = BeautifulSoup(entry.get('content', ''), 'html.parser')
        
        title = title_soup.get_text(strip=True)
        link = entry.get('entryUrl', '#')
        description = description_soup.get_text(strip=True)
        
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
