from flask import Flask, request, render_template, send_file, jsonify
import os
from converter.converter import extrair_movimentos_pdf
from PyPDF2 import PdfReader
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    
    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Converter PDF e obter OFX
            ofx_data = extrair_movimentos_pdf(file_path)
            
            if ofx_data:
                # Deleta o arquivo após o sucesso
                os.remove(file_path)
                
                # Cria um arquivo em memória
                ofx_file = io.BytesIO()
                ofx_file.write(ofx_data.encode('utf-8'))
                ofx_file.seek(0)
                
                return send_file(
                    ofx_file,
                    as_attachment=True,
                    download_name="extrato.ofx",
                    mimetype="text/plain"
                )
            else:
                return 'Não foi possível extrair os dados do PDF.', 400
        
        except Exception as e:
            # Se ocorrer um erro, retorna uma mensagem adequada
            return f'Ocorreu um erro ao processar o arquivo: {str(e)}', 500

    return 'Arquivo inválido, envie um arquivo PDF.', 400


if __name__ == '__main__':
    app.run(debug=True)
