# Transcrevendo uma imagem em texto com AWS Textract

Projeto desenvolvido a partir da atividade apresentada no vídeo da aula. A proposta é enviar uma imagem contendo uma lista de material escolar para o Amazon Textract, extrair o texto por OCR com Python e exibir os itens e suas quantidades.

## O que o projeto faz

1. Lê a imagem `lista_material_escolar.jpg`.
2. Valida formato e tamanho do arquivo.
3. Cria um cliente do Amazon Textract usando as credenciais configuradas na AWS.
4. Envia a imagem para a operação `DetectDocumentText`.
5. Recupera os blocos do tipo `LINE`.
6. Salva o texto bruto e uma versão estruturada com quantidade + item.

Para uma imagem simples de uma página, a operação síncrona `DetectDocumentText` é adequada porque retorna as linhas e palavras detectadas em uma única resposta. A documentação atual do boto3 informa suporte a JPEG, PNG, PDF e TIFF para a operação; quando os bytes são enviados diretamente pelo SDK, o formato do arquivo deve ser JPEG ou PNG e o limite informado é 5 MB. citeturn172089search0turn172089search5

## Estrutura

```text
atividade_textract/
├── lista_material_escolar.jpg
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 1. Instalar dependências

No terminal:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois:

```bash
pip install -r requirements.txt
```

## 2. Configurar a AWS

Configure suas credenciais usando o AWS CLI, sem colocar chave de acesso diretamente no código:

```bash
aws configure
```

Também é possível usar um perfil:

```bash
aws configure --profile textract
```

E executar:

PowerShell:

```powershell
$env:AWS_PROFILE="textract"
$env:AWS_REGION="us-east-1"
python main.py
```

Ou definir apenas a região:

```powershell
$env:AWS_REGION="us-east-1"
python main.py
```

A identidade configurada precisa ter permissão para usar o Amazon Textract.

## 3. Executar

```bash
python main.py
```

O programa exibirá primeiro o texto detectado e depois uma lista estruturada, por exemplo:

```text
=== TEXTO EXTRAÍDO PELO TEXTRACT ===
3 rolos de fita crepe
1 bloco de canson A4
...

=== LISTA ESTRUTURADA ===
- 3 x rolos de fita crepe
- 1 x bloco de canson A4
...
```

O resultado completo da API também é salvo em `resultado_textract.json`.

## Resultado esperado para a imagem da atividade

A imagem mostrada na aula contém uma lista com os seguintes itens:

```text
3 rolos de fita crepe
1 bloco de canson A4
1 fita adesiva
5 folhas de cartolina
3 placas de EVA
1 EVA com gliter
5 papel colorset
1 caneta permanente
1 pacote palito de sorvete
4 papel cartão
1 kit leoni n. 1
1 dicionário
1 pincel n.14
1 pasta 20mm
```

A grafia acima representa o conteúdo visível da imagem da atividade; o texto efetivamente retornado pelo Textract pode apresentar pequenas diferenças de OCR, e o arquivo `resultado_textract.json` preserva a resposta original da API.

## Evidência da proposta apresentada no vídeo

Na explicação, o professor orienta a escolher um método de extração de texto/OCR, testar o Textract pela interface web e depois desenvolver um código Python que envie a imagem ao Textract e receba de volta o conteúdo textual da lista, incluindo as quantidades dos materiais.

## Referências

- Documentação oficial do Amazon Textract – `DetectDocumentText`.
- Documentação oficial do boto3 para o cliente Textract.
- AWS CLI / referências do Amazon Textract.
