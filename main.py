import os
from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
from io import BytesIO
import mysql.connector
import logging

app = Flask(__name__)

# Configuração do banco de dados
db_config = {
    'user': 'if0_38125220',
    'password': 'SUA_SENHA',
    'host': 'sql200.infinityfree.com',
    'database': 'if0_38125220_XXX'
}

# Caminho do arquivo PDF no mesmo diretório do script
PDF_FILE_PATH = os.path.join(os.path.dirname(__file__), "rifa.pdf")

print("Arquivo PDF encontrado:", os.path.exists(PDF_FILE_PATH))

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    try:
        logging.info("Recebendo requisição para atualizar PDF")
        data = request.json
        numbers = data.get('numbers', [])
        logging.info(f"Números recebidos: {numbers}")

        if not os.path.exists(PDF_FILE_PATH):
            logging.error("Arquivo rifa.pdf não encontrado")
            return jsonify({"error": "O arquivo rifa.pdf não foi encontrado"}), 404

        pdf_document = fitz.open(PDF_FILE_PATH)
        logging.info("PDF carregado com sucesso")
        page = pdf_document[0]

        table_positions = analyze_pdf_for_table(page)
        logging.info(f"Posições da tabela identificadas: {table_positions}")

        for number in numbers:
            if number in table_positions:
                rect = table_positions[number]
                page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)

        updated_pdf = BytesIO()
        pdf_document.save(updated_pdf)
        pdf_document.close()
        updated_pdf.seek(0)
        logging.info("PDF atualizado salvo em memória")

        doc = fitz.open(stream=updated_pdf, filetype="pdf")
        pix = doc[0].get_pixmap()
        png_output = BytesIO()
        pix.save(png_output, format="png")
        png_output.seek(0)
        logging.info("PNG gerado com sucesso")

        return send_file(png_output, mimetype='image/png', as_attachment=True, download_name='updated_rifa.png')

    except Exception as e:
        logging.error(f"Erro ao processar o PDF: {str(e)}")
        return jsonify({"error": f"Erro ao processar o PDF: {str(e)}"}), 500


@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    conn.close()
    return jsonify(reservations)


@app.route('/reservations', methods=['POST'])
def save_reservation():
    data = request.json
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    for number, name in data.items():
        cursor.execute(
            "REPLACE INTO reservations (number, name) VALUES (%s, %s)",
            (number, name)
        )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


def analyze_pdf_for_table(page):
    positions = {i: fitz.Rect(50 * (i % 10), 50 * (i // 10), 50 * (i % 10 + 1), 50 * (i // 10 + 1)) for i in range(1, 101)}
    return positions


if __name__ == '__main__':
    app.run(debug=True)
