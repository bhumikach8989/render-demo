from flask import Flask, request, render_template, jsonify
import fitz  # PyMuPDF
import requests
import re
# import spacy
from bs4 import BeautifulSoup

app = Flask(__name__)
# Extract subject-predicate-object triples from text (very basic)
def extract_triples(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    triples = []
    for sentence in sentences:
        parts = re.split(r'\s+', sentence.strip())
        if len(parts) >= 3:
            triples.append({
                'source': parts[0],
                'relation': ' '.join(parts[1:-1]),
                'target': parts[-1].strip('. ')
            })
    return triples

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

# Extract text from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = ""
    if 'text' in request.form and request.form['text'].strip():
        text = request.form['text']
    elif 'url' in request.form and request.form['url'].strip():
        text = extract_text_from_url(request.form['url'])
    elif 'pdf' in request.files:
        file = request.files['pdf']
        text = extract_text_from_pdf(file)

    triples = extract_triples(text)
    return jsonify(triples)

if __name__ == '__main__':
    app.run(debug=True)