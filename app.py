from flask import Flask, request, jsonify, send_file, after_this_request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import uuid

app = Flask(__name__)

MAX_PAGES = 25

scraped_data = {}

@app.route('/')
def index():
    return send_file('index.html')

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_links(base_url, html_content, visited, pages_scraped):
    scraped_files = {}
    if pages_scraped >= MAX_PAGES:
        return pages_scraped, scraped_files
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        if pages_scraped >= MAX_PAGES:
            break
        url = urljoin(base_url, link['href'])
        if url not in visited and urlparse(base_url).netloc == urlparse(url).netloc:
            visited.add(url)
            content = fetch_html(url)
            if content:
                file_id = str(uuid.uuid4())
                scraped_files[file_id] = content
                pages_scraped += 1
                pages_scraped, more_files = scrape_links(url, content, visited, pages_scraped)
                scraped_files.update(more_files)
    return pages_scraped, scraped_files

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data['url']
    
    try:
        main_content = fetch_html(url)
        if main_content is None:
            return jsonify({'success': False})

        visited = set()
        visited.add(url)
        pages_scraped, scraped_files = scrape_links(url, main_content, visited, pages_scraped=1)
        
        main_file_id = str(uuid.uuid4())
        scraped_files[main_file_id] = main_content
        scraped_data.update(scraped_files)

        return jsonify({'success': True, 'files': list(scraped_files.keys())})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/download/<file_id>')
def download_file(file_id):
    content = scraped_data.get(file_id)
    if content:
        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
            except Exception as error:
                print(f"Error removing file: {error}")
            return response

        filename = f"{file_id}.html"
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
