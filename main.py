from flask import Flask, request, send_file
from fpdf import FPDF
from io import BytesIO
from flask_cors import CORS
import fitz  # PyMuPDF

app = Flask(__name__)

# Habilitando CORS para todas as rotas
CORS(app)

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    numbers = request.json.get('numbers', [])
    pdf_file = '/path/to/your/pdf.pdf'

    # Carrega o PDF
    pdf_document = fitz.open(pdf_file)
    page = pdf_document[0]

    # Adiciona marcadores nos números selecionados
    for number in numbers:
        rect = get_number_position(number)
        if rect:
            page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)

    # Salva o PDF atualizado
    updated_pdf = BytesIO()
    pdf_document.save(updated_pdf)
    pdf_document.close()
    updated_pdf.seek(0)

    # Converte para PNG
    doc = fitz.open(stream=updated_pdf, filetype="pdf")
    pix = doc[0].get_pixmap()
    png_output = BytesIO(pix.tobytes("png"))
    return send_file(png_output, mimetype='image/png', as_attachment=True, download_name='updated_rifa.png')

def get_number_position(number):
    # Mapear posições dos números no PDF
    positions = {
        1: (50, 50, 100, 100),  # Exemplo: posição no PDF
        # Adicione todas as outras posições aqui
    }
    return positions.get(number)

if __name__ == '__main__':
    app.run(debug=True)
