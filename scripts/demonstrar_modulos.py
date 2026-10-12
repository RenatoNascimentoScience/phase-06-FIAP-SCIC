"""Demonstre as funcionalidades novas sem modificar ou substituir o menu."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd

from src.alertas import FilaAlertas
from src.analise import gerar_analise_final
from src.busca import buscar_por_prefixo
from src.dispositivos import analisar_dispositivos, converter_bases


def demonstrar() -> dict:
    dados = pd.read_csv(RAIZ / "dados_aurora_siger.csv")
    fila = FilaAlertas(dados)
    total = len(fila)
    proximo = fila.proximo()
    retirado = fila.retirar()
    eletricos = analisar_dispositivos(dados)
    return {
        "versoes": {"python": platform.python_version(),
                    **{nome: importlib.metadata.version(nome)
                       for nome in ["numpy", "pandas", "scikit-learn"]}},
        "preservacao": {nome: hashlib.sha256((RAIZ / nome).read_bytes()).hexdigest()
                        for nome in ["codigo_fonte.py", "dados_aurora_siger.csv"]},
        "heap": {"total_inicial": total, "proximo": proximo, "retirado": retirado,
                 "total_apos_retirada": len(fila), "ordem_restante": fila.listar()},
        "trie": {"com": buscar_por_prefixo(dados, "modulo", "com").to_dict(orient="records"),
                 "MED": buscar_por_prefixo(dados, "codigo_sensor", "MED").to_dict(orient="records")},
        "bases": converter_bases(7),
        "eletricidade": {"unidades": eletricos.attrs["unidades"],
                         "primeiro_registro": eletricos.iloc[0].to_dict()},
        "analise_final": gerar_analise_final(dados),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, help="Arquivo JSON para registrar a execução.")
    argumentos = parser.parse_args()
    resultado = demonstrar()
    print(f"Registros: {resultado['analise_final']['total_registros']}")
    print(f"Alertas/manutenção na heap: {resultado['heap']['total_inicial']}")
    print(f"Mais urgente: {resultado['heap']['proximo']['registro']['codigo_sensor']}")
    print(f"Registros por prefixo: com={len(resultado['trie']['com'])}; MED={len(resultado['trie']['MED'])}")
    print(f"Bases do ciclo 7: {resultado['bases']}")
    print(f"Potência do primeiro registro: {resultado['eletricidade']['primeiro_registro']['potencia_w']:.2f} W")
    print(f"Latência média: {resultado['analise_final']['latencia_observada_media_ms']:.2f} ms")
    print("Menu original preservado; integração das opções 5 a 8 ainda pendente.")
    if argumentos.saida:
        argumentos.saida.parent.mkdir(parents=True, exist_ok=True)
        argumentos.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2,
                                               allow_nan=False) + "\n", encoding="utf-8")
        print("Evidências da execução registradas em JSON.")


if __name__ == "__main__":
    main()
