"""Prepare um ZIP candidato ou verifique os requisitos locais do pacote final."""

import argparse
import ast
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
import zipfile

RAIZ = Path(__file__).resolve().parents[1]
OBRIGATORIOS = ["codigo_fonte.py", "dados_aurora_siger.csv", "relatorio_tecnico.md",
                "README.md", "requirements.txt", "link_video.txt"]
PASTAS = ["src", "tests", "docs", "scripts"]


def pendencias_entrega(raiz: Path) -> list[str]:
    pendencias = []
    for nome in OBRIGATORIOS:
        caminho = raiz / nome
        if not caminho.is_file() or not caminho.read_bytes().strip():
            pendencias.append(f"Arquivo obrigatório ausente ou vazio: {nome}.")
    codigo = raiz / "codigo_fonte.py"
    if codigo.is_file():
        arvore = ast.parse(codigo.read_text(encoding="utf-8"))
        if any(isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
               and no.func.id == "funcionalidade_em_desenvolvimento" for no in ast.walk(arvore)):
            pendencias.append("O menu ainda chama funcionalidades em desenvolvimento.")
    video = raiz / "link_video.txt"
    if video.is_file():
        linhas = video.read_text(encoding="utf-8").strip().splitlines()
        url = urlsplit(linhas[0] if linhas else "")
        identificador = ""
        if url.scheme == "https" and url.hostname in {"youtube.com", "www.youtube.com", "youtu.be"}:
            if url.hostname == "youtu.be":
                identificador = url.path.strip("/")
            elif url.path == "/watch":
                identificador = parse_qs(url.query).get("v", [""])[0]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", identificador):
            pendencias.append("Falta registrar um link válido da apresentação no YouTube.")
    return pendencias


def preparar_pacote(raiz: Path, destino: Path, candidato: bool = False) -> list[str]:
    pendencias = pendencias_entrega(raiz)
    if pendencias and not candidato:
        raise ValueError("Entrega final indisponível: " + " ".join(pendencias))
    arquivos = [raiz / nome for nome in OBRIGATORIOS if (raiz / nome).is_file()]
    for pasta in PASTAS:
        arquivos.extend(caminho for caminho in sorted((raiz / pasta).rglob("*"))
                        if caminho.is_file() and caminho.suffix in {".py", ".md", ".json", ".txt"}
                        and "__pycache__" not in caminho.parts and not caminho.is_symlink())
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED) as pacote:
        for caminho in arquivos:
            if not caminho.resolve().is_relative_to(raiz.resolve()):
                raise ValueError("O pacote não pode incluir arquivos externos ao projeto.")
            pacote.write(caminho, "SCIC_Aurora_Siger/" + caminho.relative_to(raiz).as_posix())
        if candidato:
            pacote.writestr("SCIC_Aurora_Siger/PENDENCIAS_ENTREGA.txt",
                            "Pacote candidato para revisão.\n" + "\n".join(pendencias)
                            + "\nConfirmar manualmente duração, acesso Não listado e funcionamento do vídeo.\n")
    return pendencias


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidato", action="store_true", help="Permitir pendências explicitamente identificadas.")
    parser.add_argument("--saida", type=Path, help="Destino do ZIP.")
    argumentos = parser.parse_args()
    nome = "scic-candidato-modulos.zip" if argumentos.candidato else "scic-entrega.zip"
    destino = argumentos.saida or RAIZ / "output" / nome
    try:
        pendencias = preparar_pacote(RAIZ, destino, argumentos.candidato)
    except ValueError as erro:
        parser.exit(1, str(erro) + "\n")
    print("Pacote candidato criado." if argumentos.candidato else "Pacote criado; conferir manualmente o vídeo.")
    for pendencia in pendencias:
        print("Pendente: " + pendencia)


if __name__ == "__main__":
    main()
