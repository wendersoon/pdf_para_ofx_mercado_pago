from collections import defaultdict
from datetime import datetime
from PyPDF2 import PdfReader
import unicodedata
import json
import re

def normalize_text(text):
    """
    Normaliza o texto para remover problemas de acentuação e codificação.
    """
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

def extrair_dados_empresa(texto):
    """
    Extrai as informações da empresa do cabeçalho da primeira página.
    """
    # Expressões regulares ajustadas
    agencia_conta_pattern = r"(\d+)\s+(\d+)\s+CPF/CNPJ:"  # Captura a agência e a conta juntas antes de CPF/CNPJ
    entradas_pattern = r"Entradas:\s*R\$\s*([\d.,]+)"
    saidas_pattern = r"Saidas:\s*R\$\s*([\d.,-]+)"
    saldo_inicial_pattern = r"Saldo inicial:\s*R\$\s*([\d.,]+)"
    periodo_pattern = r"De\s*(\d{2}-\d{2}-\d{4})\s*al\s*(\d{2}-\d{2}-\d{4})"
    
    # Captura os valores correspondentes usando regex
    agencia_conta = re.search(agencia_conta_pattern, texto)
    entradas = re.search(entradas_pattern, texto)
    saidas = re.search(saidas_pattern, texto)
    saldo_inicial = re.search(saldo_inicial_pattern, texto)
    periodo = re.search(periodo_pattern, texto)
    
    # Separar agência e conta se encontrados
    agencia = agencia_conta.group(1) if agencia_conta else None
    conta = agencia_conta.group(2) if agencia_conta else None
    
    # Construindo o dicionário com os dados extraídos
    empresa = {
        "agencia": agencia,
        "conta": conta,
        "entradas": f"R$ {entradas.group(1)}" if entradas else None,
        "de": periodo.group(1) if periodo else None,
        "para": periodo.group(2) if periodo else None,
        "saidas": f"R$ {saidas.group(1)}" if saidas else None,
        "saldo_inicial": f"R$ {saldo_inicial.group(1)}" if saldo_inicial else None
    }

    return empresa
    
def extrair_movimentos(texto):
    """
    Extrai os movimentos financeiros a partir do texto.
    """
    movimentos = []

    # Padrão regex atualizado para lidar com variações no espaçamento e evitar sobreposição com dados da empresa
    padrao_movimento = re.compile(
        r'(\d{2}-\d{2}-\d{4})\s*'  # Data
        r'([^\d]+?)\s*'  # Descrição (não capturando IDs e valores)
        r'(\d+)\s*'  # ID da operação
        r'R\$ ([\d.,-]+)\s*'  # Valor
        r'R\$ ((?:\d{1,3}(?:\.\d{3})*|\d+)(?:,\d{2})?)'  # Saldo
    )

    for match in padrao_movimento.finditer(texto):
        data, descricao, id_operacao, valor, saldo = match.groups()
        descricao = " ".join(descricao.split())  # Limpar espaços extras
        movimento = {
            "data": data,
            "descricao": descricao.strip(),
            "id_operacao": id_operacao,
            "valor": f"R$ {valor}",
            "saldo": f"R$ {saldo}"
        }
        movimentos.append(movimento)

    return movimentos

def verificar_duplicidade_de_informacoes(data):
    """
        Verifica se ocorre duplicidade nos dados extraídos,
        a ducplicidade é contada a partir da ocorrência de uma
        mesma chave nos dados
    """

    # Dicionário para contar ocorrências de cada movimento
    movimento_ocorrencias = defaultdict(list)

    # Iterar sobre os movimentos
    for movimento in data['movimentos']:
        # chave única usando os campos relevantes
        CHAVE = (movimento['id_operacao'], movimento['valor'], movimento['data'])
        movimento_ocorrencias[CHAVE].append(movimento)

    # Verificar e imprimir movimentos duplicados
    duplicados = False
    for CHAVE, movimentos in movimento_ocorrencias.items():
        if len(movimentos) > 1:
            duplicados = True
            print(f"Movimentos duplicados encontrados para {CHAVE}:")
            for mov in movimentos:
                print(mov)

    if not duplicados:
        print("Nenhum movimento duplicado encontrado.")

def json_to_ofx(data):
    """
        CONVERTE O DICIONARIO RECEBiDO NO FORMATO OFX
    """

    def format_ofx_date(date_str):
        date = datetime.strptime(date_str, "%d-%m-%Y")
        return date.strftime("%Y%m%d000000")

    def format_amount(amount_str):
        return amount_str.replace("R$ ", "").replace(".", "").replace(",", ".")
    
    
    empresa = data['empresa']
    movimentos = data['movimentos']
    
    ofx_data = []
    
    ofx_data.append("OFXHEADER:100")
    ofx_data.append("DATA:OFXSGML")
    ofx_data.append("VERSION:102")
    ofx_data.append("SECURITY:NONE")
    ofx_data.append("ENCODING:USASCII")
    ofx_data.append("CHARSET:1252")
    ofx_data.append("COMPRESSION:NONE")
    ofx_data.append("OLDFILEUID:NONE")
    ofx_data.append("NEWFILEUID:NONE")
    ofx_data.append("")
    ofx_data.append("<OFX>")
    ofx_data.append("  <SIGNONMSGSRSV1>")
    ofx_data.append("    <SONRS>")
    ofx_data.append("      <STATUS>")
    ofx_data.append("        <CODE>0</CODE>")
    ofx_data.append("        <SEVERITY>INFO</SEVERITY>")
    ofx_data.append("      </STATUS>")
    ofx_data.append("      <DTSERVER>NaNNaNNaNNaNNaNNaN</DTSERVER>")
    ofx_data.append("      <LANGUAGE>ENG</LANGUAGE>")
    ofx_data.append("      <FI>")
    ofx_data.append("        <ORG>Mercado Pago</ORG>")
    ofx_data.append("        <FID>323</FID>")
    ofx_data.append("      </FI>")
    ofx_data.append("    </SONRS>")
    ofx_data.append("  </SIGNONMSGSRSV1>")
    ofx_data.append("  <BANKMSGSRSV1>")
    ofx_data.append("    <STMTTRNRS>")
    ofx_data.append("      <TRNUID>1</TRNUID>")
    ofx_data.append("      <STATUS>")
    ofx_data.append("        <CODE>0</CODE>")
    ofx_data.append("        <SEVERITY>INFO</SEVERITY>")
    ofx_data.append("      </STATUS>")
    ofx_data.append("      <STMTRS>")
    ofx_data.append("        <CURDEF>USD</CURDEF>")
    ofx_data.append("        <BANKACCTFROM>")
    ofx_data.append(f"          <BANKID>{empresa['agencia']}</BANKID>")
    ofx_data.append(f"          <ACCTID>{empresa['conta']}</ACCTID>")
    ofx_data.append("          <ACCTTYPE>CHECKING</ACCTTYPE>")
    ofx_data.append("        </BANKACCTFROM>")
    ofx_data.append("        <BANKTRANLIST>")
    ofx_data.append(f"          <DTSTART>{format_ofx_date(empresa['de'])}</DTSTART>")
    ofx_data.append(f"          <DTEND>{format_ofx_date(empresa['para'])}</DTEND>")
    
    for idx, mov in enumerate(movimentos):
        trn_type = "CREDIT" if float(format_amount(mov['valor'])) > 0 else "DEBIT"
        ofx_data.append("          <STMTTRN>")
        ofx_data.append(f"            <TRNTYPE>{trn_type}</TRNTYPE>")
        ofx_data.append(f"            <DTPOSTED>{format_ofx_date(mov['data'])}</DTPOSTED>")
        ofx_data.append(f"            <TRNAMT>{format_amount(mov['valor'])}</TRNAMT>")
        ofx_data.append(f"            <FITID>{idx}</FITID>")
        ofx_data.append(f"            <REFNUM>{mov['id_operacao']}</REFNUM>")
        ofx_data.append(f"            <MEMO>{mov['descricao']}</MEMO>")
        ofx_data.append("          </STMTTRN>")
    
    ofx_data.append("        </BANKTRANLIST>")
    ofx_data.append("      </STMTRS>")
    ofx_data.append("    </STMTTRNRS>")
    ofx_data.append("  </BANKMSGSRSV1>")
    ofx_data.append("</OFX>")
    
    return "\n".join(ofx_data)
        
def extrair_movimentos_pdf(pdf_path):
    resultado = dict()
    movimentos = []
    with open(pdf_path, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        i = 1
        for page in reader.pages:
            texto = normalize_text(page.extract_text())
            
            # Extraindo dados da empresa da primeira página
            if i ==1:
                empresa = extrair_dados_empresa(texto.replace("\n", ""))

            movimentos.extend(extrair_movimentos(texto.replace("\n", "")))
            i += 1
            
    # Montando o JSON final
    resultado = {
        "empresa": empresa,
        "movimentos": movimentos
    }
    verificar_duplicidade_de_informacoes(resultado)
    ofx_data = json_to_ofx(resultado)
    return ofx_data