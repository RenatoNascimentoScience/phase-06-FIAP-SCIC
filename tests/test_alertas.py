from pathlib import Path
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.alertas import FilaAlertas


def alerta(nome, prioridade=3, criticidade=3, essencial=0, ciclo=2, status="Alerta"):
    return {"modulo": nome, "status": status, "prioridade": prioridade,
            "criticidade": criticidade, "modulo_essencial": essencial, "ciclo": ciclo}


class TestFilaAlertas(unittest.TestCase):
    def test_ordem_de_insercao_nao_substitui_prioridade(self):
        fila = FilaAlertas()
        for registro in [alerta("baixo", 1), alerta("alto", 5), alerta("medio", 3)]:
            self.assertTrue(fila.inserir(registro))
        self.assertEqual([fila.retirar()["registro"]["modulo"] for _ in range(3)],
                         ["alto", "medio", "baixo"])

    def test_todos_os_desempates(self):
        casos = [
            (alerta("primeiro", 4), alerta("segundo", 3, 5, 1, 1)),
            (alerta("primeiro", criticidade=4), alerta("segundo", criticidade=3, essencial=1, ciclo=1)),
            (alerta("primeiro", essencial=1), alerta("segundo", essencial=0, ciclo=1)),
            (alerta("primeiro", ciclo=1), alerta("segundo", ciclo=2)),
        ]
        for primeiro, segundo in casos:
            with self.subTest(primeiro=primeiro):
                fila = FilaAlertas(pd.DataFrame([segundo, primeiro]))
                self.assertEqual(fila.retirar()["registro"]["modulo"], "primeiro")

    def test_empate_completo_preserva_insercao_sem_comparar_dicionarios(self):
        fila = FilaAlertas(pd.DataFrame([alerta("A"), alerta("B")]))
        fila.inserir(alerta("C"))
        self.assertEqual([item["registro"]["modulo"] for item in fila.listar()], ["A", "B", "C"])

    def test_apenas_alerta_e_manutencao_entram_na_fila(self):
        fila = FilaAlertas(pd.DataFrame([
            alerta("A"), alerta("M", status="Manutenção"), alerta("normal", status="Ativo")]))
        self.assertEqual(len(fila), 2)
        self.assertFalse(fila.inserir(alerta("normal", status="ativo")))

    def test_consultar_listar_e_copiar_nao_consumem_original(self):
        fila = FilaAlertas(pd.DataFrame([alerta("A"), alerta("B")]))
        proximo = fila.proximo()
        proximo["registro"]["modulo"] = "alterado"
        self.assertEqual(fila.proximo()["registro"]["modulo"], "A")
        self.assertEqual(len(fila.listar()), 2)
        copia = fila.copiar()
        copia.retirar()
        copia.inserir(alerta("novo", 5))
        self.assertEqual(len(fila), 2)
        self.assertEqual(fila.proximo()["registro"]["modulo"], "A")

    def test_registro_recebido_nao_fica_compartilhado(self):
        registro = alerta("A")
        fila = FilaAlertas()
        fila.inserir(registro)
        registro["modulo"] = "alterado"
        self.assertEqual(fila.retirar()["registro"]["modulo"], "A")

    def test_fila_vazia(self):
        fila = FilaAlertas()
        self.assertIsNone(fila.proximo())
        self.assertIsNone(fila.retirar())
        self.assertEqual(fila.listar(), [])

    def test_campos_invalidos(self):
        for campo, valor in [("prioridade", -1), ("criticidade", 1.5),
                             ("modulo_essencial", 2), ("ciclo", 0), ("status", "desconhecido")]:
            with self.subTest(campo=campo):
                registro = alerta("A")
                registro[campo] = valor
                with self.assertRaises(ValueError):
                    FilaAlertas().inserir(registro)
        with self.assertRaises(ValueError):
            FilaAlertas().inserir({})

    def test_base_real_e_preservacao(self):
        dados = pd.read_csv(Path(__file__).resolve().parents[1] / "dados_aurora_siger.csv")
        original = dados.copy(deep=True)
        fila = FilaAlertas(dados)
        self.assertEqual(len(fila), 10)
        self.assertEqual(fila.proximo()["registro"]["codigo_sensor"], "COM-01")
        resultado = fila.retirar()
        self.assertEqual(resultado["criterios"]["prioridade"], 5)
        self.assertIn("criticidade 5", resultado["justificativa"])
        assert_frame_equal(dados, original)


if __name__ == "__main__":
    unittest.main()
