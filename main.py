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

# Habilitando CORS para todas as rotas
CORS(app)

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    data = request.json
    pdf_url = data.get('pdf_url')
    numbers = data.get('numbers', [])
    
    # Baixar o PDF da URL
    pdf_content = requests.get(pdf_url).content
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    
    # Analisar o conteúdo do PDF e encontrar a tabela com os números
    page = pdf_document[0]  # Analisando a primeira página
    table_positions = analyze_pdf_for_table(page)  # Função para detectar posições dos números na tabela
    
    # Adiciona marcadores nos números selecionados
    for number in numbers:
        if number in table_positions:
            rect = table_positions[number]
            page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)
    
    # Salva o PDF atualizado
    updated_pdf = BytesIO()
    pdf_document.save(updated_pdf)
    pdf_document.close()
    updated_pdf.seek(0)

    # Converte para PNG
    doc = fitz.open(stream=updated_pdf, filetype="pdf")
    pix = doc[0].get_pixmap()
    png_output = IOBytes(pix.tobytes("png"))
    
    return send_file(png_output, mimetype='image/png', as_attachment=True, download_name='updated_rifa.png')

def analyze_pdf_for_table(page):
    """Função para identificar as posições dos números na tabela"""
    # Usar OCR para tentar identificar a tabela e os números
    img = page.get_pixmap()
    img_bytes = img.tobytes("png")
    
    # Usando pytesseract para tentar detectar números na imagem
    img_pil = Image.open(IOBytes(img_bytes))
    text = pytesseract.image_to_string(img_pil)
    
    # Encontrar os números dentro do texto
    numbers_found = extract_numbers_from_text(text)
    
    # Mapear as posições dos números (exemplo heurístico)
    positions = {}
    for number in numbers_found:
        # A lógica para encontrar as posições deve ser ajustada de acordo com a tabela
        # Por exemplo, procurando números entre 1 e 100
        if 1 <= int(number) <= 100:
            positions[int(number)] = (50, 50, 100, 100)  # Exemplo de posição, a ser ajustada
    return positions

def extract_numbers_from_text(text):
    """Extrair números da string obtida pelo OCR"""
    numbers = []
    for word in text.split():
        if word.isdigit():
            numbers.append(word)
    return numbers

if __name__ == '__main__':
    app.run(debug=True)
