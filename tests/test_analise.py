import json
from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from src.analise import gerar_analise_final


class TestAnaliseFinal(unittest.TestCase):
    def setUp(self):
        self.dados = pd.read_csv(Path(__file__).resolve().parents[1] / "dados_aurora_siger.csv")

    def test_contagens_e_resumo_conferidos(self):
        resultado = gerar_analise_final(self.dados)
        self.assertEqual(resultado["total_registros"], 48)
        self.assertEqual(resultado["registros_por_status"], {"Ativo": 38, "Manutencao": 5, "Alerta": 5})
        self.assertEqual(set(resultado["registros_por_modulo"].values()), {8})
        self.assertEqual(resultado["total_alertas_priorizados"], 10)
        self.assertAlmostEqual(resultado["latencia_observada_media_ms"], 174.8125)
        self.assertAlmostEqual(resultado["resumo_eletrico"]["potencia_maxima_w"], 22.9 * 3.3)

    def test_prioridades_e_recomendacoes_apontam_mesmos_registros(self):
        resultado = gerar_analise_final(self.dados)
        alertas = resultado["alertas_mais_urgentes"]
        self.assertEqual([a["registro"]["codigo_sensor"] for a in alertas],
                         ["COM-01", "MED-01", "DAT-02", "AGR-02", "LAB-01"])
        for alerta, proposta in zip(alertas, resultado["recomendacoes"]):
            self.assertEqual(proposta["codigo_sensor"], alerta["registro"]["codigo_sensor"])
            self.assertEqual(proposta["ciclo"], alerta["registro"]["ciclo"])
            self.assertEqual(proposta["justificativa"], alerta["justificativa"])
            self.assertIn("operador", proposta["acao_proposta"])
        self.assertIn("redundante", resultado["recomendacoes"][0]["acao_proposta"])

    def test_base_sem_alertas(self):
        dados = self.dados[self.dados.status == "Ativo"]
        resultado = gerar_analise_final(dados)
        self.assertEqual(resultado["total_alertas_priorizados"], 0)
        self.assertEqual(resultado["recomendacoes"], [])
        self.assertGreater(resultado["resumo_eletrico"]["potencia_media_w"], 0)

    def test_base_vazia_nao_produz_nan_ou_recomendacao_sem_evidencia(self):
        resultado = gerar_analise_final(self.dados.head(0))
        self.assertEqual(resultado["total_registros"], 0)
        self.assertEqual(resultado["recomendacoes"], [])
        self.assertEqual(resultado["condicoes_por_modulo"], [])
        self.assertIsNone(resultado["resumo_eletrico"]["potencia_media_w"])
        json.dumps(resultado, allow_nan=False)

    def test_zero_na_latencia_nao_exige_erro_relativo(self):
        dados = self.dados.head(1).copy()
        dados.loc[dados.index[0], "latencia_observada_ms"] = 0
        self.assertEqual(gerar_analise_final(dados)["latencia_observada_media_ms"], 0)

    def test_preserva_dados_e_nao_interage_com_terminal(self):
        original = self.dados.copy(deep=True)
        with patch("builtins.input", side_effect=AssertionError("Entrada indevida")), \
             patch("builtins.print", side_effect=AssertionError("Saída indevida")):
            resultado = gerar_analise_final(self.dados)
        assert_frame_equal(self.dados, original)
        json.dumps(resultado, allow_nan=False)
        self.assertTrue(resultado["validacao_humana"])
        self.assertTrue(any("causa e efeito" in frase for frase in resultado["limitacoes"]))

    def test_colunas_ausentes_e_valores_invalidos(self):
        with self.assertRaises(ValueError):
            gerar_analise_final(self.dados.drop(columns=["modulo"]))
        for campo, valor in [("modulo", ""), ("codigo_sensor", None), ("latencia_observada_ms", -1)]:
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                dados = self.dados.head(1).copy()
                dados.loc[dados.index[0], campo] = valor
                gerar_analise_final(dados)


if __name__ == "__main__":
    unittest.main()
