# Conversor de Extrato PDF para OFX - Mercado Pago

## Resumo
Este projeto é uma aplicação web desenvolvida com Flask que permite a conversão de arquivos PDF de extrato bancário para o formato OFX (Open Financial Exchange). O formato OFX é amplamente utilizado para a troca de informações financeiras entre diferentes sistemas e softwares, facilitando a integração e automação de processos contábeis e financeiros. Infelizmente, o Mercado Pago não fornece extratos no formato OFX, o que motiva a necessidade desta ferramenta.

## Estrutura do Projeto

```
├── app.py                 # Arquivo principal da aplicação Flask
├── converter              # Diretório com o módulo de conversão
│   ├── converter.py       # Código para extração e conversão de dados PDF para OFX
├── LICENSE                # Arquivo de licença do projeto
├── README.md              # Este arquivo
├── requirements.txt       # Dependências do projeto
├── templates              # Diretório com o template HTML
│   └── upload.html        # Página para upload e conversão de arquivos PDF
```

## Tecnologias Empregadas
<p>
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,flask,javascript,css,html,bootstrap" />
  </a>
</p>


## Como Usar

* Clone o repositório:
```
git clone https://github.com/wendersoon/pdf_para_ofx_mercado_pago.git
```

* Instale as dependências:
```
pip install -r requirements.txt
```

* Execute a aplicação:

```
flask run
```
* Acesse a aplicação
Abra um navegador e vá para http://localhost:5000.

* Utilize o formulário de upload
 Selecione um arquivo PDF de extrato bancário do mercado pago e envie-o para converter para o formato OFX.

## Contribuições

Contribuições são bem-vindas! Se você encontrar algum bug ou deseja adicionar novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença
Este projeto está licenciado sob a Licença [MIT](https://github.com/wendersoon/pdf_para_ofx_mercado_pago/blob/main/LICENSE).