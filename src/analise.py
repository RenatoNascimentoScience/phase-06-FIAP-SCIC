"""Síntese operacional baseada nos registros e nas regras do protótipo."""

import pandas as pd

from ._validacao import coluna_numerica, normalizar_texto, validar_colunas
from .alertas import COLUNAS_ALERTAS, FilaAlertas
from .dispositivos import analisar_dispositivos


LIMITACOES = [
    "Dados simulados: os resultados não comprovam desempenho de uma rede real.",
    "Prioridades são regras internas, não um modelo de risco treinado nem limites universais.",
    "Variações de tensão e latência não demonstram, isoladamente, relação de causa e efeito.",
    "Potência de alimentação em W não é energia em Wh nem potência irradiada por uma antena.",
    "Sem duração dos ciclos, não é possível estimar energia consumida ou comparar instantes físicos.",
    "Não há medição de redundância, falhas físicas, capacidade de baterias ou geração de uma microrrede.",
    "A avaliação da regressão permanece na opção 4; esta síntese não recalcula suas métricas.",
    "Toda recomendação exige revisão humana antes de alterar a operação.",
]


def _agregado(serie: pd.Series, operacao: str) -> float | None:
    return float(getattr(serie, operacao)()) if not serie.empty else None


def gerar_analise_final(dados: pd.DataFrame) -> dict:
    """Retorne contagens, cinco alertas prioritários e interpretação contextual.

    As recomendações são propostas de inspeção e planejamento. Não há atuação
    sobre dispositivos nem treinamento de outro modelo neste módulo.
    """
    colunas = COLUNAS_ALERTAS + ["modulo", "codigo_sensor", "latencia_observada_ms",
                               "latencia_prevista_ms", "tensao_v", "corrente_a"]
    validar_colunas(dados, colunas)
    for campo in ["modulo", "codigo_sensor"]:
        for valor in dados[campo]:
            if not normalizar_texto(valor):
                raise ValueError(f"O campo '{campo}' não pode conter texto vazio.")
    observada = coluna_numerica(dados, "latencia_observada_ms")
    coluna_numerica(dados, "latencia_prevista_ms")
    eletricos = analisar_dispositivos(dados)
    fila = FilaAlertas(dados)
    alertas = fila.listar()[:5]

    condicoes = []
    medias_por_modulo = {}
    for modulo, grupo in eletricos.groupby("modulo", sort=False):
        status = grupo["status"].map(normalizar_texto)
        potencia_media = float(grupo["potencia_w"].mean())
        medias_por_modulo[modulo] = potencia_media
        condicoes.append({
            "modulo": modulo,
            "registros": len(grupo),
            "registros_em_alerta": int((status == "alerta").sum()),
            "registros_em_manutencao": int((status == "manutencao").sum()),
            "latencia_maxima_ms": float(grupo["latencia_observada_ms"].max()),
            "tensao_minima_v": float(grupo["tensao_v"].min()),
            "tensao_maxima_v": float(grupo["tensao_v"].max()),
            "potencia_media_w": potencia_media,
        })

    recomendacoes = []
    for alerta in alertas:
        registro = alerta["registro"]
        recomendacoes.append({
            "modulo": registro["modulo"],
            "codigo_sensor": registro["codigo_sensor"],
            "ciclo": int(registro["ciclo"]),
            "evidencias": {
                "latencia_observada_ms": float(registro["latencia_observada_ms"]),
                "latencia_prevista_ms": float(registro["latencia_prevista_ms"]),
                "tensao_v": float(registro["tensao_v"]),
                "corrente_a": float(registro["corrente_a"]),
            },
            "justificativa": alerta["justificativa"],
            "acao_proposta": (
                "Conferir sensor, enlace e alimentação; comparar novas leituras "
                "e registrar recorrência para planejar manutenção. "
                + ("Avaliar conceitualmente um enlace redundante por se tratar de módulo essencial. "
                   if alerta["criterios"]["modulo_essencial"] else
                   "Planejar inspeção considerando o impacto no módulo. ")
                + "O operador deve validar os dados e a ação antes de atuar."
            ),
        })

    return {
        "total_registros": len(dados),
        "registros_por_status": {str(k): int(v) for k, v in dados["status"].value_counts(sort=False).items()},
        "registros_por_modulo": {str(k): int(v) for k, v in dados["modulo"].value_counts(sort=False).items()},
        "total_alertas_priorizados": len(fila),
        "alertas_mais_urgentes": alertas,
        "latencia_observada_media_ms": _agregado(observada, "mean"),
        "resumo_eletrico": {
            "potencia_media_w": _agregado(eletricos["potencia_w"], "mean"),
            "potencia_maxima_w": _agregado(eletricos["potencia_w"], "max"),
            "tensao_minima_v": _agregado(eletricos["tensao_v"], "min"),
            "tensao_maxima_v": _agregado(eletricos["tensao_v"], "max"),
            "corrente_media_a": _agregado(eletricos["corrente_a"], "mean"),
            "potencia_media_por_modulo_w": medias_por_modulo,
        },
        "condicoes_por_modulo": condicoes,
        "recomendacoes": recomendacoes,
        "gerenciamento_comunicacao": {
            "monitoramento": "Comparar status, latência e alimentação a cada leitura; não presumir normalidade sem dados recentes.",
            "automacao": "A heap organiza atendimento e a trie localiza registros; nenhuma delas executa transporte ou atuação remota.",
            "armazenamento_redundancia": "Manter histórico das decisões e avaliar enlaces alternativos para módulos essenciais, sem assumir independência entre falhas.",
            "manutencao": "Usar recorrência e inspeção para planejar manutenção; a base não contém histórico suficiente para prever falhas físicas.",
            "microrredes": "Relacionar disponibilidade de energia e comunicação; reserva, geração e autonomia exigiriam medições adicionais.",
        },
        "validacao_humana": "Revisar dados, prioridades e consequências antes de autorizar uma ação; registrar a justificativa da decisão.",
        "limitacoes": list(LIMITACOES),
    }
