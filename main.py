import os
from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
from io import BytesIO
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir requisições de outros domínios

PDF_FILE_PATH = os.path.join(os.path.dirname(__file__), "Story Instagram Rifa Solidária Moderno Azul.pdf")

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    try:
        data = request.json
        numbers = data.get('numbers', [])
        if not os.path.exists(PDF_FILE_PATH):
            return jsonify({"error": "O arquivo PDF não foi encontrado"}), 404

        pdf_document = fitz.open(PDF_FILE_PATH)
        page = pdf_document[0]

        # Ajustar posições com base no layout do PDF
        table_positions = analyze_pdf_for_table(page)

        for number in numbers:
            if number in table_positions:
                rect = table_positions[number]
                page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)

        updated_pdf = BytesIO()
        pdf_document.save(updated_pdf)
        pdf_document.close()
        updated_pdf.seek(0)

        # Converter PDF para PNG
        doc = fitz.open(stream=updated_pdf, filetype="pdf")
        pix = doc[0].get_pixmap()
        png_output = BytesIO()
        pix.save(png_output, format="png")
        png_output.seek(0)

        return send_file(png_output, mimetype='image/png', as_attachment=True, download_name='updated_rifa.png')

    except Exception as e:
        return jsonify({"error": f"Erro ao processar o PDF: {str(e)}"}), 500


def analyze_pdf_for_table(page):
    """Ajuste as coordenadas com base no layout real do PDF."""
    positions = {}
    start_x, start_y = 50, 100  # Coordenadas iniciais
    box_width, box_height = 50, 50  # Tamanho de cada número
    for i in range(1, 101):
        col = (i - 1) % 10
        row = (i - 1) // 10
        x0 = start_x + col * box_width
        y0 = start_y + row * box_height
        x1 = x0 + box_width
        y1 = y0 + box_height
        positions[i] = fitz.Rect(x0, y0, x1, y1)
    return positions


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
