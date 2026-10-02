import json
import os
import re
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, ProfileNotFound


IMAGE_PATH = Path(__file__).with_name("lista_material_escolar.jpg")
RAW_OUTPUT = Path(__file__).with_name("resultado_textract.json")
TEXT_OUTPUT = Path(__file__).with_name("resultado.txt")
STRUCTURED_OUTPUT = Path(__file__).with_name("resultado_estruturado.json")


MAX_BYTES = 5 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def create_textract_client():
    """Cria o cliente AWS Textract usando credenciais configuradas na máquina."""
    region = os.getenv("AWS_REGION", "us-east-1")
    profile = os.getenv("AWS_PROFILE")

    try:
        if profile:
            session = boto3.Session(profile_name=profile, region_name=region)
        else:
            session = boto3.Session(region_name=region)

        return session.client("textract")
    except ProfileNotFound as exc:
        raise RuntimeError(
            f"O perfil AWS '{profile}' não foi encontrado. "
            "Configure-o com 'aws configure --profile SEU_PERFIL' ou remova AWS_PROFILE."
        ) from exc


def validate_image(path: Path) -> None:
    """Valida formato e tamanho antes de enviar a imagem ao Textract."""
    if not path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Use uma imagem JPEG ou PNG para este projeto.")

    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(
            f"A imagem possui {size / 1024 / 1024:.2f} MB. "
            "O limite para bytes enviados diretamente ao Textract é 5 MB."
        )


def extract_text(client, image_path: Path) -> dict:
    """Envia a imagem ao Amazon Textract e retorna a resposta completa."""
    image_bytes = image_path.read_bytes()
    return client.detect_document_text(Document={"Bytes": image_bytes})


def get_lines(response: dict) -> list[str]:
    """Retorna somente os blocos do tipo LINE, mantendo a ordem devolvida pelo Textract."""
    return [
        block["Text"]
        for block in response.get("Blocks", [])
        if block.get("BlockType") == "LINE" and block.get("Text")
    ]


def parse_school_list(lines: list[str]) -> list[dict]:
    """Tenta separar quantidade e descrição dos itens da lista."""
    items = []

    for line in lines:
        clean = re.sub(r"\s+", " ", line).strip()
        match = re.match(r"^[.·•\-\s]*(\d+)\s+(.+)$", clean)

        if match:
            quantity = int(match.group(1))
            description = match.group(2).strip()
            items.append({"quantidade": quantity, "item": description})
        else:
            items.append({"quantidade": None, "item": clean})

    return items


def save_results(response: dict, lines: list[str], items: list[dict]) -> None:
    RAW_OUTPUT.write_text(
        json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    TEXT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    STRUCTURED_OUTPUT.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    validate_image(IMAGE_PATH)
    client = create_textract_client()

    print("Enviando imagem para o Amazon Textract...\n")

    try:
        response = extract_text(client, IMAGE_PATH)
    except NoCredentialsError as exc:
        raise RuntimeError(
            "Credenciais AWS não encontradas. Execute 'aws configure' "
            "ou configure as variáveis de ambiente da AWS."
        ) from exc
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"Erro ao chamar o Amazon Textract: {exc}") from exc

    lines = get_lines(response)
    items = parse_school_list(lines)
    save_results(response, lines, items)

    print("=== TEXTO EXTRAÍDO PELO TEXTRACT ===")
    for line in lines:
        print(line)

    print("\n=== LISTA ESTRUTURADA ===")
    for item in items:
        if item["quantidade"] is None:
            print(f"- {item['item']}")
        else:
            print(f"- {item['quantidade']} x {item['item']}")

    print(f"\nArquivos gerados:")
    print(f"- {RAW_OUTPUT.name}")
    print(f"- {TEXT_OUTPUT.name}")
    print(f"- {STRUCTURED_OUTPUT.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERRO: {exc}")
        raise SystemExit(1)
