from flask import Flask, request, send_file
from fpdf import FPDF
from io import BytesIO
from flask_cors import CORS
import fitz  # PyMuPDF
import requests
import pytesseract
from PIL import Image
from io import BytesIO as IOBytes

app = Flask(__name__)
CORS(app)

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    data = request.json
    pdf_url = data.get('pdf_url')
    numbers = data.get('numbers', [])
    
    # Baixar o PDF da URL
    pdf_content = requests.get(pdf_url).content
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    
    # Analisar o PDF para identificar a tabela
    page = pdf_document[0]
    table_positions = analyze_pdf_for_table(page)

    # Marcar os números selecionados
    for number in numbers:
        if number in table_positions:
            rect = table_positions[number]
            page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)
    
    # Salvar PDF atualizado
    updated_pdf = BytesIO()
    pdf_document.save(updated_pdf)
    pdf_document.close()
    updated_pdf.seek(0)

    # Converter PDF para PNG
    doc = fitz.open(stream=updated_pdf, filetype="pdf")
    pix = doc[0].get_pixmap()
    png_output = IOBytes(pix.tobytes("png"))
    
    return send_file(png_output, mimetype='image/png', as_attachment=True, download_name='updated_rifa.png')

def analyze_pdf_for_table(page):
    """Identifica posições dos números na tabela"""
    img = page.get_pixmap()
    img_bytes = img.tobytes("png")
    
    img_pil = Image.open(IOBytes(img_bytes))
    text = pytesseract.image_to_string(img_pil)
    
    numbers_found = extract_numbers_from_text(text)
    positions = {}
    for number in numbers_found:
        if 1 <= int(number) <= 100:
            positions[int(number)] = (50, 50, 100, 100)  # Exemplo: ajustar para o layout do PDF
    return positions

def extract_numbers_from_text(text):
    """Extrai números do texto"""
    return [int(word) for word in text.split() if word.isdigit()]

if __name__ == '__main__':
    app.run(debug=True)
