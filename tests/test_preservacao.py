"""Verifique a preservação das funções anteriores e do CSV da demonstração."""

import ast
import hashlib
import json
from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class TestPreservacao(unittest.TestCase):
    def test_funcoes_anteriores_preservadas(self):
        manifesto = json.loads((RAIZ / "tests/preservacao_original.json").read_text(encoding="utf-8"))
        fonte = (RAIZ / "codigo_fonte.py").read_text(encoding="utf-8")
        funcoes = {no.name: no for no in ast.parse(fonte).body if isinstance(no, ast.FunctionDef)}
        for nome, esperado in manifesto["funcoes"].items():
            with self.subTest(funcao=nome):
                trecho = ast.get_source_segment(fonte, funcoes[nome])
                self.assertEqual(hashlib.sha256(trecho.encode("utf-8")).hexdigest(), esperado)

    def test_csv_preservado(self):
        manifesto = json.loads((RAIZ / "tests/preservacao_original.json").read_text(encoding="utf-8"))
        atual = hashlib.sha256((RAIZ / "dados_aurora_siger.csv").read_bytes()).hexdigest()
        self.assertEqual(atual, manifesto["dados_aurora_siger_sha256"])


if __name__ == "__main__":
    unittest.main()
