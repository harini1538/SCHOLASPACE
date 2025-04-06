import fitz  # PyMuPDF for handling PDFs
from flask import Flask, render_template, request, jsonify,Blueprint
import requests
import re
import os

doubt_bp = Blueprint('chat', __name__ , template_folder='templates')

@doubt_bp.route('/doubt')
def doubt():
    return render_template('doubt.html')
@doubt_bp.route('/chat', methods=['POST'])
def chat():
    try:
        # Get user input (PDF URL and page number)
        pdf_url = request.form['pdf_url']
        page_number = int(request.form['page_number']) - 1  # PyMuPDF pages are 0-indexed

        # Download the PDF
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_file = "temp_book.pdf"
            with open(pdf_file, 'wb') as f:
                f.write(response.content)
        else:
            return jsonify({'response': 'Failed to download PDF. Check the URL and try again.'})

        # Open the PDF file
        doc = fitz.open(pdf_file)

        if page_number >= doc.page_count:
            return jsonify({'response': 'Invalid page number.'})

        # Extract context from a specific page based on a word
        def extract_context(page, word, window=100):
            text = page.get_text()
            word_index = text.lower().find(word.lower())
            if word_index != -1:
                start = max(0, word_index - window)
                end = min(len(text), word_index + len(word) + window)
                return text[start:end].replace('\n', ' ').strip()
            return ""

        # Load the specified page
        page = doc.load_page(page_number)
        blocks = page.get_text("dict")["blocks"]
        bold_words = {}

        # Loop through text blocks and extract bold words
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["flags"] == 20:  # Bold text has a font flag of 20 in PyMuPDF
                            bold_text = span["text"]
                            bold_text_words = re.findall(r'\w+', bold_text)
                            if bold_text_words:
                                bold_word = bold_text_words[0]
                                context = extract_context(page, bold_word)
                                if context:
                                    bold_words[bold_word] = context

        doc.close()

        # Prepare the response text for bold words and their descriptions
        if bold_words:
            response_text = "Bold Words and Their Descriptions from the Book:\n\n"
            for word, description in bold_words.items():
                response_text += f"• {word}\n  Description: {description[:500]}...\n\n"  # Limit description length
        else:
            response_text = "No bold words found on the specified page."

        # Clean up the temporary PDF file
        if os.path.exists(pdf_file):
            os.remove(pdf_file)

        return jsonify({'response': response_text})

    except requests.RequestException as req_err:
        return jsonify({'response': f'Network error: {req_err}'})
    except Exception as e:
        return jsonify({'response': f'An unexpected error occurred: {e}'})


