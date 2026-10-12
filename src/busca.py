"""Índice trie para consultas por prefixo de módulos e sensores."""

from dataclasses import dataclass, field

import pandas as pd

from ._validacao import inteiro_do_registro, normalizar_texto, validar_colunas


@dataclass
class _NoTrie:
    filhos: dict[str, "_NoTrie"] = field(default_factory=dict)
    posicoes: set[int] = field(default_factory=set)


class TrieRegistros:
    """Compartilhe prefixos e associe termos completos a posições de registros."""

    def __init__(self):
        self._raiz = _NoTrie()

    def inserir(self, termo: str, posicao: int) -> None:
        normalizado = normalizar_texto(termo)
        posicao = inteiro_do_registro(posicao, "posicao")
        no = self._raiz
        for caractere in normalizado:
            if caractere not in no.filhos:
                no.filhos[caractere] = _NoTrie()
            no = no.filhos[caractere]
        no.posicoes.add(posicao)

    def buscar(self, prefixo: str) -> list[int]:
        """Percorra o prefixo e seus descendentes; devolva posições únicas."""
        no = self._raiz
        for caractere in normalizar_texto(prefixo):
            if caractere not in no.filhos:
                return []
            no = no.filhos[caractere]
        posicoes = set()
        pendentes = [no]
        # Percurso iterativo evita depender do limite de recursão do Python.
        while pendentes:
            atual = pendentes.pop()
            posicoes.update(atual.posicoes)
            pendentes.extend(atual.filhos.values())
        return sorted(posicoes)


def buscar_por_prefixo(dados: pd.DataFrame, campo: str, prefixo: str) -> pd.DataFrame:
    """Retorne os registros encontrados sem modificar a base ou sua escrita.

    O índice é reconstruído para a base recebida, evitando resultados obsoletos
    após recarregar dados. Localizar o nó custa O(p), para prefixo de tamanho p;
    enumerar e ordenar resultados também tem custo. Não é busca por substring.
    """
    if campo not in {"modulo", "codigo_sensor"}:
        raise ValueError("Escolha o campo 'modulo' ou 'codigo_sensor'.")
    validar_colunas(dados, [campo])
    normalizar_texto(prefixo)
    trie = TrieRegistros()
    for posicao, termo in enumerate(dados[campo]):
        trie.inserir(termo, posicao)
    return dados.iloc[trie.buscar(prefixo)].copy(deep=True)
