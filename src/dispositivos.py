"""Bases numéricas e potência elétrica de alimentação dos dispositivos."""

from numbers import Integral

import pandas as pd

from ._validacao import coluna_numerica, validar_colunas


UNIDADES_ELETRICAS = {"tensao_v": "V", "corrente_a": "A", "potencia_w": "W"}


def converter_bases(valor: int) -> dict:
    """Converta um inteiro não negativo; não trunque floats nem aceite booleanos."""
    if isinstance(valor, bool) or not isinstance(valor, Integral) or valor < 0:
        raise ValueError("Informe um inteiro não negativo para a conversão de bases.")
    inteiro = int(valor)
    return {"decimal": inteiro, "binario": format(inteiro, "b"),
            "hexadecimal": format(inteiro, "X")}


def analisar_dispositivos(dados: pd.DataFrame) -> pd.DataFrame:
    """Calcule P = V × I em uma cópia, com unidades explícitas nos metadados.

    A base representa alimentação elétrica em corrente contínua. O resultado
    não mede potência irradiada por uma antena nem energia consumida em Wh.
    """
    validar_colunas(dados, ["tensao_v", "corrente_a"])
    tensao = coluna_numerica(dados, "tensao_v")
    corrente = coluna_numerica(dados, "corrente_a")
    resultado = dados.copy(deep=True)
    resultado["potencia_w"] = tensao * corrente
    unidades = dict(resultado.attrs.get("unidades", {}))
    unidades.update(UNIDADES_ELETRICAS)
    resultado.attrs["unidades"] = unidades
    return resultado

