import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from src.dispositivos import analisar_dispositivos, converter_bases


class TestBases(unittest.TestCase):
    def test_zero_e_ciclo_sete(self):
        self.assertEqual(converter_bases(0), {"decimal": 0, "binario": "0", "hexadecimal": "0"})
        self.assertEqual(converter_bases(7), {"decimal": 7, "binario": "111", "hexadecimal": "7"})

    def test_hexadecimal_e_ida_e_volta(self):
        for valor in [26, 255, 1024, np.int64(7)]:
            with self.subTest(valor=valor):
                convertido = converter_bases(valor)
                self.assertEqual(int(convertido["binario"], 2), int(valor))
                self.assertEqual(int(convertido["hexadecimal"], 16), int(valor))
        self.assertEqual(converter_bases(26)["hexadecimal"], "1A")

    def test_rejeitar_entradas_incompativeis(self):
        for valor in [-1, 7.0, 1.5, "7", True, None, np.nan]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                converter_bases(valor)


class TestEletricidade(unittest.TestCase):
    def test_calculo_manual_e_unidades(self):
        dados = pd.DataFrame({"tensao_v": [12.0, 24.0, 0.0], "corrente_a": [0.5, 2.1, 2.0]})
        resultado = analisar_dispositivos(dados)
        for atual, esperado in zip(resultado.potencia_w, [6.0, 50.4, 0.0]):
            self.assertAlmostEqual(atual, esperado)
        self.assertEqual(resultado.attrs["unidades"],
                         {"tensao_v": "V", "corrente_a": "A", "potencia_w": "W"})

    def test_preserva_colunas_indices_e_dados(self):
        dados = pd.DataFrame({"modulo": ["A", "B"], "tensao_v": [12, 24],
                              "corrente_a": [0.5, 1.5]}, index=[4, 4])
        dados.attrs["unidades"] = {"ciclo": "registro"}
        original = dados.copy(deep=True)
        resultado = analisar_dispositivos(dados)
        self.assertEqual(resultado.potencia_w.tolist(), [6.0, 36.0])
        self.assertEqual(resultado.modulo.tolist(), ["A", "B"])
        resultado.attrs["unidades"]["ciclo"] = "alterado"
        resultado.iloc[0, 0] = "alterado"
        assert_frame_equal(dados, original)
        self.assertEqual(dados.attrs, original.attrs)

    def test_valores_invalidos(self):
        for valor in [-1, np.inf, np.nan, "12", True, 1 + 2j]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                analisar_dispositivos(pd.DataFrame({"tensao_v": [valor], "corrente_a": [1.0]}))
        with self.assertRaises(ValueError):
            analisar_dispositivos(pd.DataFrame({"corrente_a": [1.0]}))
        with self.assertRaises(ValueError):
            analisar_dispositivos(pd.DataFrame({"tensao_v": pd.Series([pd.NA], dtype="Float64"),
                                                "corrente_a": [1.0]}))

    def test_base_vazia(self):
        resultado = analisar_dispositivos(pd.DataFrame(columns=["tensao_v", "corrente_a"]))
        self.assertTrue(resultado.empty)
        self.assertIn("potencia_w", resultado.columns)


if __name__ == "__main__":
    unittest.main()
