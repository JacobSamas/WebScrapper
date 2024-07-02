from flask import Flask, request, jsonify, send_from_directory, send_file
from bs4 import BeautifulSoup
import requests
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data['url']
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        headings = soup.find_all('h1')
        heading_texts = [heading.get_text() for heading in headings]
        
        # Save to JSON
        json_path = 'headings.json'
        with open(json_path, 'w') as json_file:
            json.dump(heading_texts, json_file)
        
        return jsonify({'success': True, 'headings': heading_texts, 'json': json_path})
    except requests.RequestException as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
