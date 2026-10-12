"""Fila de prioridade de alertas da Aurora Siger."""

from collections.abc import Mapping
from copy import deepcopy
import heapq

import pandas as pd

from ._validacao import inteiro_do_registro, normalizar_texto, validar_colunas


COLUNAS_ALERTAS = ["status", "prioridade", "criticidade", "modulo_essencial", "ciclo"]


class FilaAlertas:
    """Min-heap com sinais invertidos para atender prioridades maiores primeiro.

    Construir a fila custa O(n); inserir ou retirar custa O(log n). Consultar
    a raiz custa O(1). Listar todos os alertas custa O(n log n) e usa uma cópia.
    """

    def __init__(self, dados: pd.DataFrame | None = None):
        self._heap: list[tuple] = []
        self._sequencia = 0
        if dados is not None:
            validar_colunas(dados, COLUNAS_ALERTAS)
            for registro in dados.to_dict(orient="records"):
                entrada = self._preparar(registro)
                if entrada is not None:
                    self._heap.append(entrada)
            heapq.heapify(self._heap)

    def __len__(self) -> int:
        return len(self._heap)

    def _preparar(self, registro: Mapping) -> tuple | None:
        if not isinstance(registro, Mapping):
            raise ValueError("O alerta deve ser um registro com campos nomeados.")
        faltantes = [campo for campo in COLUNAS_ALERTAS if campo not in registro]
        if faltantes:
            raise ValueError("Campos do alerta ausentes: " + ", ".join(faltantes))
        status = normalizar_texto(registro["status"])
        if status == "ativo":
            return None
        if status not in {"alerta", "manutencao"}:
            raise ValueError("Status esperado: Ativo, Alerta ou Manutencao.")
        prioridade = inteiro_do_registro(registro["prioridade"], "prioridade")
        criticidade = inteiro_do_registro(registro["criticidade"], "criticidade")
        essencial = inteiro_do_registro(registro["modulo_essencial"], "modulo_essencial")
        if essencial not in {0, 1}:
            raise ValueError("O campo 'modulo_essencial' deve ser 0 ou 1.")
        ciclo = inteiro_do_registro(registro["ciclo"], "ciclo", minimo=1)
        ordem = self._sequencia
        self._sequencia += 1
        # A sequência única impede comparar os dicionários quando há empate.
        return (-prioridade, -criticidade, -essencial, ciclo, ordem, deepcopy(dict(registro)))

    @staticmethod
    def _resultado(entrada: tuple) -> dict:
        prioridade, criticidade, essencial, ciclo, ordem, registro = entrada
        criterios = {
            "prioridade": -prioridade,
            "criticidade": -criticidade,
            "modulo_essencial": -essencial,
            "ciclo": ciclo,
            "ordem_insercao": ordem,
        }
        return {
            "registro": deepcopy(registro),
            "criterios": criterios,
            "justificativa": (
                f"Prioridade {-prioridade}; criticidade {-criticidade}; "
                f"módulo essencial: {'sim' if essencial == -1 else 'não'}; ciclo {ciclo}. "
                "Comparação nessa ordem, com números maiores primeiro nos três "
                "primeiros critérios, ciclo menor primeiro e ordem de inserção no empate."
            ),
        }

    def inserir(self, registro: Mapping) -> bool:
        entrada = self._preparar(registro)
        if entrada is None:
            return False
        heapq.heappush(self._heap, entrada)
        return True

    def proximo(self) -> dict | None:
        return self._resultado(self._heap[0]) if self._heap else None

    def retirar(self) -> dict | None:
        return self._resultado(heapq.heappop(self._heap)) if self._heap else None

    def copiar(self) -> "FilaAlertas":
        copia = FilaAlertas()
        copia._heap = deepcopy(self._heap)
        copia._sequencia = self._sequencia
        return copia

    def listar(self) -> list[dict]:
        copia = self.copiar()
        resultados = []
        while copia:
            resultados.append(copia.retirar())
        return resultados
