from flask import Flask, request, jsonify, send_from_directory, send_file
import requests
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
        
        # Get the whole HTML content
        html_content = response.text
        
        # Save to an HTML file
        html_path = 'scraped_page.html'
        with open(html_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        
        return jsonify({'success': True, 'html': html_path})
    except requests.RequestException as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/html")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404

if __name__ == '__main__':
    app.run(debug=True)
