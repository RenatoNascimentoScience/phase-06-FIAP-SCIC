from pathlib import Path
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.busca import TrieRegistros, buscar_por_prefixo


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.dados = pd.DataFrame({
            "modulo": [" Comunicação   Central ", "Comando", "Suporte Médico", "Comunicação Central"],
            "codigo_sensor": ["COM-01", "CMD-01", "MED-01", "COM-02"],
            "ciclo": [1, 1, 1, 2],
        }, index=[7, 7, 9, 7])

    def test_caixa_acentos_e_espacos(self):
        resultado = buscar_por_prefixo(self.dados, "modulo", "  COMUNICAÇÃO  ")
        self.assertEqual(resultado.codigo_sensor.tolist(), ["COM-01", "COM-02"])
        self.assertEqual(resultado.iloc[0].modulo, " Comunicação   Central ")

    def test_sensor(self):
        self.assertEqual(buscar_por_prefixo(self.dados, "codigo_sensor", "med").codigo_sensor.tolist(), ["MED-01"])

    def test_palavra_completa_e_prefixo_nao_sao_substrings(self):
        self.assertEqual(len(buscar_por_prefixo(self.dados, "modulo", "Comando")), 1)
        self.assertTrue(buscar_por_prefixo(self.dados, "modulo", "mando").empty)
        self.assertEqual(len(buscar_por_prefixo(self.dados, "modulo", "com")), 3)

    def test_prefixo_inexistente_preserva_colunas(self):
        resultado = buscar_por_prefixo(self.dados, "modulo", "xyz")
        self.assertTrue(resultado.empty)
        self.assertEqual(resultado.columns.tolist(), self.dados.columns.tolist())

    def test_prefixo_vazio_devolve_todos_na_ordem_original(self):
        assert_frame_equal(buscar_por_prefixo(self.dados, "modulo", "  "), self.dados)

    def test_indice_repetido_nao_duplica_ou_perde_registros(self):
        resultado = buscar_por_prefixo(self.dados, "modulo", "com")
        self.assertEqual(resultado.codigo_sensor.tolist(), ["COM-01", "CMD-01", "COM-02"])
        self.assertEqual(resultado.index.tolist(), [7, 7, 7])

    def test_reinsercao_na_trie_nao_duplica_posicao(self):
        trie = TrieRegistros()
        trie.inserir("Comando", 2)
        trie.inserir("COMANDO", 2)
        trie.inserir("Comunicação", 0)
        self.assertEqual(trie.buscar("com"), [0, 2])
        self.assertEqual(trie.buscar("Comando"), [2])

    def test_resultado_independente(self):
        original = self.dados.copy(deep=True)
        resultado = buscar_por_prefixo(self.dados, "modulo", "com")
        resultado.iloc[0, 0] = "alterado"
        assert_frame_equal(self.dados, original)

    def test_base_vazia(self):
        vazio = self.dados.head(0)
        assert_frame_equal(buscar_por_prefixo(vazio, "modulo", "com"), vazio)

    def test_entradas_invalidas(self):
        for campo, prefixo in [("status", "com"), ("modulo", None)]:
            with self.subTest(campo=campo, prefixo=prefixo), self.assertRaises(ValueError):
                buscar_por_prefixo(self.dados, campo, prefixo)
        with self.assertRaises(ValueError):
            buscar_por_prefixo(pd.DataFrame(), "modulo", "com")
        with self.assertRaises(ValueError):
            buscar_por_prefixo(pd.DataFrame({"modulo": [None]}), "modulo", "com")

    def test_base_real(self):
        dados = pd.read_csv(Path(__file__).resolve().parents[1] / "dados_aurora_siger.csv")
        self.assertEqual(len(buscar_por_prefixo(dados, "modulo", "com")), 8)
        self.assertEqual(len(buscar_por_prefixo(dados, "codigo_sensor", "MED")), 8)


if __name__ == "__main__":
    unittest.main()
