"""Validações compartilhadas pelos módulos novos, sem alterar a base original."""

import math
import unicodedata
from numbers import Integral, Real

import pandas as pd


def normalizar_texto(texto: str) -> str:
    """Ignore caixa, acentos e espaços excedentes somente na comparação."""
    if not isinstance(texto, str):
        raise ValueError("O texto de consulta deve ser uma string.")
    decomposicao = unicodedata.normalize("NFKD", texto.casefold())
    sem_acentos = "".join(c for c in decomposicao if not unicodedata.combining(c))
    return " ".join(sem_acentos.split())


def validar_colunas(dados: pd.DataFrame, colunas: list[str]) -> None:
    if not isinstance(dados, pd.DataFrame):
        raise ValueError("Informe os dados em um DataFrame do Pandas.")
    if not dados.columns.is_unique:
        raise ValueError("A base contém nomes de colunas duplicados.")
    faltantes = [coluna for coluna in colunas if coluna not in dados.columns]
    if faltantes:
        raise ValueError("Colunas necessárias ausentes: " + ", ".join(faltantes))


def inteiro_do_registro(valor: object, campo: str, minimo: int = 0) -> int:
    """Aceite inteiros ou números integrais lidos do CSV; rejeite ausências."""
    if isinstance(valor, bool) or not isinstance(valor, (Integral, Real)):
        raise ValueError(f"O campo '{campo}' deve ser um inteiro >= {minimo}.")
    if not math.isfinite(valor) or valor < minimo or valor != int(valor):
        raise ValueError(f"O campo '{campo}' deve ser um inteiro >= {minimo}.")
    return int(valor)


def coluna_numerica(dados: pd.DataFrame, campo: str) -> pd.Series:
    """Valide valores reais, finitos e não negativos, mantendo o DataFrame."""
    validar_colunas(dados, [campo])
    coluna = dados[campo]
    if coluna.empty:
        return coluna.astype(float)
    if coluna.isna().any():
        raise ValueError(f"O campo '{campo}' não pode conter valores ausentes.")
    if not pd.api.types.is_numeric_dtype(coluna) or pd.api.types.is_bool_dtype(coluna):
        raise ValueError(f"O campo '{campo}' deve conter números reais.")
    if pd.api.types.is_complex_dtype(coluna):
        raise ValueError(f"O campo '{campo}' deve conter números reais.")
    if not coluna.map(lambda valor: math.isfinite(valor) and valor >= 0).all():
        raise ValueError(f"O campo '{campo}' deve conter números finitos e não negativos.")
    return coluna.astype(float)
