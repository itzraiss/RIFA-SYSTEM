import os
from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
from io import BytesIO

app = Flask(__name__)

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

        # Verificar se o arquivo PDF existe
        if not os.path.exists(PDF_FILE_PATH):
            logging.error("Arquivo rifa.pdf não encontrado")
            return jsonify({"error": "O arquivo rifa.pdf não foi encontrado"}), 404

        # Abrir o PDF localmente
        pdf_document = fitz.open(PDF_FILE_PATH)
        logging.info("PDF carregado com sucesso")

        # Processar a primeira página
        page = pdf_document[0]

        # Exemplo de posições (ajustar conforme a lógica do seu layout)
        table_positions = analyze_pdf_for_table(page)
        logging.info(f"Posições da tabela identificadas: {table_positions}")

        # Marcar os números selecionados
        for number in numbers:
            if number in table_positions:
                rect = table_positions[number]
                page.draw_rect(rect, color=(0, 1, 0), fill=(0, 1, 0), width=0)

        # Salvar PDF atualizado em memória
        updated_pdf = BytesIO()
        pdf_document.save(updated_pdf)
        pdf_document.close()
        updated_pdf.seek(0)
        logging.info("PDF atualizado salvo em memória")

        # Converter PDF para PNG
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


def analyze_pdf_for_table(page):
    """Exemplo: lógica para identificar as posições dos números"""
    # Exemplo de posições fictícias para os números
    positions = {i: fitz.Rect(50 * (i % 10), 50 * (i // 10), 50 * (i % 10 + 1), 50 * (i // 10 + 1)) for i in range(1, 101)}
    return positions


if __name__ == '__main__':
    app.run(debug=True)
