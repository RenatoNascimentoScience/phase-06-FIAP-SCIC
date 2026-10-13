import os
import pandas as pd
import numpy as np
from pathlib import Path # Manipular caminhos com POO independente do SO

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.alertas import FilaAlertas
from src.busca import buscar_por_prefixo
from src.dispositivos import analisar_dispositivos, converter_bases
from src.analise import gerar_analise_final

# Caminho da pasta onde o arquivo Python está localizado
pasta_projeto = Path(__file__).resolve().parent

# Arquivo de dados .CSV utilizado no projeto
arquivo_dados = pasta_projeto / "dados_aurora_siger.csv"

# Função para limpar o terminal
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

# Função para aguardar o usuário apertar "ENTER" para voltar ao menu principal
def enter():
    input("\nPressione 'ENTER' para voltar ao menu principal...")

# Carregado a base de dados simulados da Aurora Siger a partir do .CSV
def carregar_dados(exibir_mensagem=False): # Define se o sistema mostra a informação de carregamento.
    try:
        dados = pd.read_csv(arquivo_dados)
        
        print("\nDados da Aurora Siger carregados com sucesso.")
        print(f"Registros Carregados: {len(dados)}")
        print(f"Colunas Encontradas: {len(dados.columns)}")

        return dados
    
    except FileNotFoundError:
        print("\nERRO: o arquivo 'dados_aurora_siger.csv' não foi encontrado.")
        print("Matenha o arquivo CSV na mesma posta de 'codigo_fonte.py'.")

    except pd.errors.EmptyDataError:
        print("\nERRO: o arquivo CSV está vazio.")

    except pd.errors.ParserError:
        print("\nERRO: não foi possível interpretar o conteúdo do arquivo CSV.")

    return None

# Exibindo uma visao simples da base carregada - Menu 1
def visualizar_dados(dados):
    if dados is None:
        print("\nNenhum dado est[a disponível para visualização.")
        return
    
    print("\n" + "=" * 60)
    print("DADOS OPERACIONAIS E DE COMUNICAÇÃO - AURORA SIGER")
    print("=" * 60)

    # Exibindo os primeiros 10 registros para não poluir o terminal
    print("\nPrimeiros 10 registros:")
    print(dados.head(10).to_string(index=False))

    print("\nResumo da Base:")
    print(f"Total de Registros: {len(dados)}")
    print(f"Total de Módulos: {dados['modulo'].nunique()}")
    print(f"Total de Sensores: {dados['codigo_sensor'].nunique()}")

    print("\nRegistros por Status:")
    print(dados["status"].value_counts().to_string())

# Função para consultar os registros - Menu 2
def consultar_registros(dados):
    if dados is None:
        print("\nNenhum dado está disponível para consulta.")
        return
    
    while True:
        limpar_tela()

        print("\n" + "=" * 60)
        print("CONSULTAR REGISTROS - AURORA SIGER")
        print("=" * 60)

        print("1 - Pesquisar por Módulo")
        print("2 - Pesquisar por Sensor")
        print("3 - Pesquisar por Status")
        print("4 - Pesquisar por Ciclo")
        print("0 - Voltar")
        print("=" * 60)

        opcao_consulta = input("Escolha o tipo de consulta: ").strip()

        # Colunas principais que serão mostradas
        colunas_exibicao = [
            "ciclo",
            "modulo",
            "codigo_sensor",
            "latencia_prevista_ms",
            "latencia_observada_ms",
            "status",
            "prioridade",
            "criticidade",
            "mensagem_alerta"
        ]

        resultado = None

        # Consulta por módulo
        if opcao_consulta == "1":
            limpar_tela()

            print("=" * 60)
            print("CONSULTA POR MÓDULO")
            print("=" * 60)

            print("\nMódulos disponíveis:")

            for modulo in dados["modulo"].unique():
                print(f"- {modulo}")

            pesquisa = input("\nDigite o nome do módulo: ".strip())

            resultado = dados[
                dados["modulo"].str.contains(
                    pesquisa,
                    case=False,
                    na=False
                )
            ]
        
        # Consulta por sensor
        elif opcao_consulta == "2":
            limpar_tela()

            print("=" * 60)
            print("CONSULTA POR SENSOR")
            print("=" * 60)

            print("\nSensores Disponíveis:")

            for sensor in sorted(dados["codigo_sensor"].unique()):
                print(f"- {sensor}")

            pesquisa = input("\nDigite o código do sensor: ").strip()

            resultado = dados[
                dados["codigo_sensor"].str.lower() == pesquisa.lower()
            ]

        # Consulta por status
        elif opcao_consulta == "3":
            limpar_tela()

            print("=" * 60)
            print("CONSULTA POR STATUS")
            print("=" * 60)

            print("\nStatus Disponíveis:")
            print("- Ativo")
            print("- Manutenção")
            print("- Alerta")

            pesquisa = input("\nDigite o status: ").strip()

            resultado = dados[
                dados["status"].str.lower() == pesquisa.lower()
            ]

        # Colsunta por ciclo
        elif opcao_consulta == "4":
            limpar_tela()

            print("=" * 60)
            print("CONSULTA POR CICLO")
            print("=" * 60)

            try:
                ciclo = int(input("\nDigite o ciclo de 1 a 8: "))

                resultado = dados[
                    dados["ciclo"] == ciclo
                ]
            
            except ValueError:
                print("\nCiclo inválido. Digite um número inteiro.")
                return

        # Voltar sem realizar consulta
        elif opcao_consulta == "0":
            return
        else:
            print("\nOpção de consulta inválida.")
            enter()
            continue
        
        # Exibindo o resultado da pesquisa
        if not resultado.empty:
            print("\nMÓDULOS ENCONTRADOS:")
            
            for modulo in sorted(resultado["modulo"].unique()):
                print(f"- {modulo}")

            print("\n" + "=" * 60)
            print(f"REGISTROS ENCONTRADOS: {len(resultado)}")
            print("=" * 60)

            print(resultado[colunas_exibicao].to_string(index=False)) # Transforma tabela Pandas em texto.
        else:
            print("\nNenhum registro encontrado.")

        enter()
    
# Classificando o erro relativo de acordo com critérios simulados - Menu 3
def classificar_erro_relativo(erro_relativo):
    if erro_relativo <= 5:
        return "Baixo"
    elif erro_relativo <= 15:
        return "Atenção"
    else:
        return "Preocupante"
    
# Função para calcular os indicadores operacionais e erros numéricos
def calcular_indicadores_erros(dados):
    if dados is None:
        print("\nNenhum dado está dispon[ivel para análise.")
        return dados
    
    # Cria uma cópia para preservar os dados originais carregados
    dados_calculados = dados.copy()

    # Calculando a potência aproximada dos dispositivos
    dados_calculados["potencia_w"] = (
        dados_calculados["tensao_v"] * dados_calculados["corrente_a"]
    ).round(2)

    # Calculando o erro absoluto entre a latência prevista e a latência observada
    dados_calculados["erro_absoluto_ms"] = (
        dados_calculados["latencia_observada_ms"] - dados_calculados["latencia_prevista_ms"]
    ).abs()

    # Calculando o erro relativo em porcentagem
    dados_calculados["erro_relativo_pct"] = (
        (
            dados_calculados["erro_absoluto_ms"] / dados_calculados["latencia_observada_ms"]
        ) * 100
    ).round(2)

    # Classificando o erro relativo
    dados_calculados["classificacao_erro"] = (
        dados_calculados["erro_relativo_pct"].apply(classificar_erro_relativo)
    )

    limpar_tela()

    print("=" * 70)
    print("INDICADORES OPERACIONAIS E ERROS NUMÉRICOS - AURORA SIGER")
    print("=" * 70)

    # Indicadores gerais
    latencia_media = dados_calculados["latencia_observada_ms"].mean()
    potencia_media = dados_calculados["potencia_w"].mean()
    erro_absoluto_medio = dados_calculados["erro_absoluto_ms"].mean()
    erro_relativo_medio = dados_calculados["erro_relativo_pct"].mean()

    print("\nRESUMO GERAL")
    print("-" * 70)
    print(f"Registros Analisados: {len(dados_calculados)}")
    print(f"Latência Observada Média: {latencia_media:.2f}ms")
    print(f"Potência Média Aproximada: {potencia_media:.2f}W")
    print(f"Erro Absoluto Médio: {erro_absoluto_medio:.2f}ms")
    print(f"Erro Relativo Médio: {erro_relativo_medio:.2f}%")

    # Quantidade de registros por classificação
    print("\nCLASSIFICAÇÃO DOS ERROS")
    print("-" * 70)

    quantidade_baixo = (
        dados_calculados["classificacao_erro"] == "Baixo"
    ).sum()

    quantidade_atencao = (
        dados_calculados["classificacao_erro"] == "Atenção"
    ).sum()

    quantidade_preocupante = (
        dados_calculados["classificacao_erro"] == "Preocupante"
    ).sum()

    print(f"Baixo: {quantidade_baixo}")
    print(f"Atenção: {quantidade_atencao}")
    print(f"Preocupante: {quantidade_preocupante}")

    print("\nCritérios Simulados Utilizados pelo SCIC:")
    print("Até 5% ----------> Baixo")
    print("Acima de 5% -----> Atenção")
    print("Acima de 15% ----> Preocupante")

    # Mosntrando os registros com maiores erros relativos
    maiores_erros = dados_calculados.sort_values(
        by="erro_relativo_pct",
        ascending=False
    ).head(10)

    colunas_exibicao = [
        "ciclo",
        "modulo",
        "codigo_sensor",
        "latencia_prevista_ms",
        "latencia_observada_ms",
        "potencia_w",
        "erro_absoluto_ms",
        "erro_relativo_pct",
        "classificacao_erro"
    ]

    print("\n 10 REGISTROS COM MAIOR ERRO RELATIVO")
    print("-" * 70)
    print(maiores_erros[colunas_exibicao].to_string(index=False))

    # Identificando o maior erro encontrado
    indice_maior_erro = dados_calculados["erro_relativo_pct"].idxmax()
    maior_erro = dados_calculados.loc[indice_maior_erro]

    print("\nMAIOR DESVIO ENCONTRADO")
    print("-" * 70)
    print(f"Módulo: {maior_erro['modulo']}")
    print(f"Sensor: {maior_erro['codigo_sensor']}")
    print(f"Latência Prevista: {maior_erro['latencia_prevista_ms']}ms")
    print(f"Latência Observada: {maior_erro['latencia_observada_ms']}ms")
    print(f"Erro Absoluto: {maior_erro['erro_absoluto_ms']:.2f}ms")
    print(f"Erro Relativo: {maior_erro['erro_relativo_pct']:.2f}%")
    print(f"Classificação: {maior_erro['classificacao_erro']}")

    # Demonstração simples da precisão do ponto flutuante
    print("\nPRECISÃO NUMÉRICA E PONTO FLUTUANTE")
    print("-" * 70)

    exemplo_ponto_flutuante = 0.1 + 0.2

    print(f"No Python, 0.1 + 0.2 resulta em: {exemplo_ponto_flutuante}")
    print(f"Arredondando para 2 casas: {exemplo_ponto_flutuante:.2f}")

    print(
    """
Pequenas diferenças podem ocorrer por que alguns números decimais não possuem
representação binária exata. Por isso, os indicadores do SCIC são arredondados
para facilitar a apresentação e interpretação.
    """
    )

    print("\nINTERPRETAÇÃO")
    print("-" * 70)

    print(
        """
Erros baixos indicam que a latência observada permaneceu próxima da estimativa.
Erros maiores exigem atenção porque podem indicar instabilidade ou anomalias na comunicação.
Os limites usados nesta simulação são critérios internos do protótipo SCIC e não representam limites universais.
        """
    )

    return dados_calculados

# Função para executar e avaliar o modelo simples de previsão - Menu 4
def executar_modelo_previsao(dados):
    if dados is None:
        print("\nNenhum dado está disponível para o modelo.")
        return
    
    print("=" * 70)
    print("MODELO SIMPLES DE PREVISÃO DE LATÊNCIA - AURORA SIGER")
    print("=" * 70)

    # Variáveis utilizadas pelo modelo
    variaveis_entrada = [
        "latencia_prevista_ms",
        "tensao_v",
        "corrente_a",
        "ciclo"
    ]

    variavel_resposta = "latencia_observada_ms"

    # dropna() para remover evetuais registros incompletos apenas nas colunas
    dados_modelo = dados[variaveis_entrada + [variavel_resposta]].dropna()

    # X contendo as variáveis utilizadas para realizar a previsão
    X = dados_modelo[variaveis_entrada]

    # y contendo o valor que é desejado prever
    y = dados_modelo[variavel_resposta]

    # Dividindo os dados - 75% para treino e 25% para teste
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42
    )

    # Criando o modelo de regressão linear
    modelo = LinearRegression()

    # Treinando o modelo utilizando os dados de treinamento
    modelo.fit(X_treino, y_treino)

    # Realizando previsões utilizando os dados de teste
    previsoes = modelo.predict(X_teste)

    # Calculando as métricas de avaliação
    mae = mean_absolute_error(y_teste, previsoes)
    mse = mean_squared_error(y_teste, previsoes)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_teste, previsoes)

    # Baseline para prever sempre a média da latência do conjunto utilizado no treinamento
    media_treino = y_treino.mean()

    previsoes_baseline = np.full(len(y_teste), media_treino)

    mae_baseline = mean_absolute_error(y_teste, previsoes_baseline)

    rmse_baseline = np.sqrt(mean_squared_error(y_teste, previsoes_baseline))

    # Exibindo os resultados
    print("\nOBJETIVO DO MODELO")
    print("-" * 70)

    print("Prever a latência observada de comunicação dos módulos da Aurora Siger")

    print("\nVariáveis de Entrada:")

    for variavel in variaveis_entrada:
        print(f"- {variavel}")

    print(f"\nVariável Prevista:")
    print(f"- {variavel_resposta}")

    print("\nDIVISÃO DOS DADOS")
    print("-" * 70)

    print(f"Total de Registros: {len(dados_modelo)}")
    print(f"Registros de Treinamento: {len(X_treino)}")
    print(f"Registros de Teste: {len(X_teste)}")

    print("\nMÉTRICAS DO MODELO")
    print("-" * 70)

    print(f"MAE:.........{mae:.2f}ms")
    print(f"MSE:.........{mse:.2f}")
    print(f"RMSE:........{rmse:.2f}ms")
    print(f"R²:..........{r2:.4f}")

    # Comparação com o baseline
    print("\nCOMPARAÇÃO COM BASELINE")
    print("-" * 70)

    print("O baseline utiliza apenas a média das latências do conjunto de treinamento.")

    print(f"\nMAE do modelo:.......{mae:.2f}ms")
    print(f"MAE do baseline:.......{mae_baseline:.2f}ms")
    print(f"\nRMSE do modelo:......{rmse:.2f}ms")
    print(f"RMSE do baseline:......{rmse_baseline:.2f}ms")

    if mae < mae_baseline:
        print("\nO modelo apresentou erro médio menor que o baseline.")
    else:
        print("\nO modelo não apresentou melhora em relação ao baseline.")

    # Exemplos de previsão
    comparacao = pd.DataFrame({
        "latencia_real_ms": y_teste.values,
        "latencia_prevista_modelo_ms": previsoes
    })

    comparacao["latencia_prevista_modelo_ms"] = (
        comparacao["latencia_prevista_modelo_ms"].round(2)
    )

    print("\nEXEMPLO DE PREVISÕES")
    print("-" * 70)

    print(comparacao.head(5).to_string(index=False))

    # Interpretação
    print("\nINTERPRETAÇÃO DAS MÉTRICAS")
    print("-" * 70)

    print(f"O MAE indica que as previsões apresentam, em média, "
          f"um erro absoluto de aproximadamente {mae:.2f}ms."  
    )

    print(
        f"\nO RMSE foi de {rmse:.2f}ms. Como essa métrica "
        "penaliza mais os erros elevados, ela ajuda a identificar "
        "a influência de previsões com desvios maiores."
    )

    if rmse > mae:
        print(
            "\nO RMSE ficou acima do MAE, indicando que alguns "
            "registros apresentaram erros maiores que a média."
        )

    print(f"\nO R² obtido foi {r2:.4f}.")

    if r2 >= 0.80:
        print(
            "Neste conjunto simulado, o modelo explicou uma parcela "
            "elevada da variação da latência."
        )
    elif r2 >= 0.50:
        print(
            "Neste conjunto simulado, o modelo explicou uma parcela "
            "moderada da variação da latência."
        )
    else:
        print(
            "Neste conjunto simulado, o modelo apresentou capacidade "
            "limitada de explicar a variação da latência."
        )
    
    print(
        "\nUm R² alto não significa que o modelo esteja perfeito. "
        "As métricas devem ser interpretadas em conjunto."
    )

# Função de análise e priorização de alertas utilizando heap - Menu 5
def analisar_alertas_prioridade(dados):
    if dados is None:
        print("\nNenhum dado está disponível para análise.")
        return
    
    print("=" * 70)
    print("PRIORIZAÇÃO DE ALERTAS COM HEAP - AURORA SIGER")
    print("=" * 70)

    # Selecionando somente os registros que precisam de atenção
    registros_alertas = dados[
        dados["status"].isin(["Alerta", "Manutencao"]) # isin() verifica se os valores da coluna pertencem a uma lista de valores específicos
    ]

    if registros_alertas.empty:
        print("\nNenhum alerta ou registro em manutenção foi encontrado.")
        return 
    
    # Criando a fila de prioridade src/alertas.py
    fila_alertas = FilaAlertas()

    # Inserindo cada registro na estrutura heap
    for _, registro in registros_alertas.iterrows(): # iterrows() percorre o DF linha por linha, permitindo acessar os valores de cada registro individualmente
        fila_alertas.inserir(registro.to_dict())

    print(f"\nRegistros priorizados: {len(registros_alertas)}")

    print("\nCRITÉRIOS DE PRIORIDADE")
    print("-" * 70)
    print("1 - Prioridade")
    print("2 - Criticidade")
    print("3 - Módulo Essencial")
    print("4 - Ciclo do Registro")

    # Recuperando o alerta de maior prioridade
    resultado_urgente = fila_alertas.proximo()

    if resultado_urgente is not None:
        alerta_urgente = resultado_urgente["registro"]

        print("\nALERTA MAIS URGENTE")
        print("-" * 70)

        print(f"Módulo: {alerta_urgente['modulo']}")
        print(f"Sensor: {alerta_urgente['codigo_sensor']}")
        print(f"Status: {alerta_urgente['status']}")
        print(f"Ciclo: {alerta_urgente['ciclo']}")
        print(f"Prioridade: {alerta_urgente['prioridade']}")
        print(f"Criticidade: {alerta_urgente['criticidade']}")

        essencial = (
            "Sim"
            if alerta_urgente["modulo_essencial"] == 1
            else "Não"
        )

        print(f"Módulo Essencial: {essencial}")
        print(f"Latência Prevista: {alerta_urgente['latencia_prevista_ms']}ms")
        print(f"Latência Observada: {alerta_urgente['latencia_observada_ms']}ms")
        print(f"Mensagem: {alerta_urgente['mensagem_alerta']}")

        # Mostrando os alertas organizados pela prioridade do heap
        alertas_ordenados = [item["registro"] for item in fila_alertas.listar()]

        print("\nFILA DE ALERTAS PRIORIZADA")
        print("-" * 70)

        for posicao, alerta in enumerate(alertas_ordenados, start=1):
            essencial = (
                "Sim"
                if alerta["modulo_essencial"] == 1
                else "Não"
            )

            print(
                f"{posicao}. "
                f"{alerta['modulo']} | "
                f"Sensor: {alerta['codigo_sensor']} | "
                f"Prioridade: {alerta['prioridade']} | "
                f"Criticidade: {alerta['criticidade']} | "
                f"Essencial: {essencial}"
            )

        print("\nPOR QUE UTILIZAR HEAP?")
        print("-" * 70)

        print(
            "Uma lista simples armazena os alertas, mas pode exigir "
            "uma busca ou ordenação para identificar o mais urgente."
        )

        print(
            "O heap mantém os registros organizados de acordo com "
            "a prioridade, permitindo acessar de forma eficiente "
            "o alerta mais urgente."
        )

# Função para buscar registros por prefixo utilizando Trie - Menu 6
def buscar_registros_prefixo(dados):
    if dados is None:
        print("\nNenhum dado está disponível para busca.")
        return
    
    # Mantém o submenu em execução até o usuário escolher 0 - Voltar
    while True:
        limpar_tela()
        
        print("=" * 70)
        print("BUSCA DE REGISTROS POR PREFIXO COM TRIE - AURORA SIGER")
        print("=" * 70)

        print("1 - Buscar por Nome do Módulo")
        print("2 - Buscar por Código do Sensor")
        print("0 - Voltar")
        print("=" * 70)

        opcao_busca = input("Escolha o tipo de busca: ").strip()

        # volta ao menu principal
        if opcao_busca == "0":
            return
        
        # Define em qual coluna a Trie realizara a pesquisa
        if opcao_busca == "1":
            campo = "modulo"
            descricao = "modulo"
        elif opcao_busca == "2":
            campo = "codigo_sensor"
            descricao = "sensor"
        else:
            print("\nOpção inválida.")
            enter()
            continue

        limpar_tela()

        print("=" * 70)
        print(f"BUSCA POR PREFIXO - {descricao.upper()}")
        print("=" * 70)

        prefixo = input(f"\nDigite o prefixo do {descricao}: ").strip()

        # Evitando que a busca vazia mostre todos os 48 registros
        if prefixo == "":
            print("\nDigite pelo menos um caractere para realizar a busca.")
            enter()
            continue

        try:
            resultado = buscar_por_prefixo( # Implementando a Trie - src/busca.py
                dados,
                campo,
                prefixo
            )
        except ValueError as erro:
            print(f"\nErro ao realizar a busca: {erro}")
            enter()
            continue

        # Verificando se algum registro foi encontrado
        if resultado.empty:
            print(f"Nenhum registro encontrado com o prefixo '{prefixo}'.")

        else:
            print("\n" + "=" * 70)
            print(f"REGISTROS ENCONTRADOS: {len(resultado)}")
            print("=" * 70)

            colunas_exibicao = [
                "ciclo",
                "modulo",
                "codigo_sensor",
                "latencia_prevista_ms",
                "latencia_observada_ms",
                "status",
                "prioridade",
                "criticidade",
                "mensagem_alerta"
            ]

            print(resultado[colunas_exibicao].to_string(index=False))

        print("\nCOMO A TRIE REALIZA A BUSCA?")
        print("-" * 70)

        print("A Trie organiza palavras e códigos compartilhando os caracteres iniciais.")

        print(
            "Assim, o sistema percorre o prefixo informado e localiza "
            "os registros associados àquele caminho."
        )

        print(
            "Essa estrutura é especialmente adequada para pesquisas "
            "por prefixo, como nomes de módulos e códigos de sensores."
        )

        enter()


#Função para analisar os dispositivos e converter as bases numéricas - Menu 7
def exibir_bases_eletricidade(dados):
    if dados is None:
        print("\nNenhum dado está disponível para análise.")
        enter()
        return
 
    # Submenu mantido em execução até o usuário escolher 0 - Voltar
    while True:
        limpar_tela()
 
        print("=" * 70)
        print("BASES NUMÉRICAS E DADOS ELÉTRICOS - AURORA SIGER")
        print("=" * 70)
 
        print("1 - Converter Valor entre Bases Numéricas")
        print("2 - Analisar Dados Elétricos (Tensão, Corrente e Potência)")
        print("3 - Dispositivos de Entrada e Saída")
        print("0 - Voltar")
        print("=" * 70)
 
        opcao_bases = input("Escolha uma opção: ").strip()
 
        if opcao_bases == "0":
            return
        elif opcao_bases == "1":
            converter_valor_bases(dados)
        elif opcao_bases == "2":
            analisar_dados_eletricos(dados)
        elif opcao_bases == "3":
            exibir_dispositivos_entrada_saida()
        else:
            print("\nOpção inválida.")
 
        enter()
 
# Conversão decimal -> binário -> hexadecimal utilizando src/dispositivos.py
def converter_valor_bases(dados):
    limpar_tela()
 
    print("=" * 70)
    print("CONVERSÃO ENTRE BASES NUMÉRICAS")
    print("=" * 70)
 
    # Exemplo automático: os ciclos da base representados nas três bases
    print("\nCICLOS DA BASE EM DECIMAL, BINÁRIO E HEXADECIMAL")
    print("-" * 70)
    print(f"{'Decimal':>8} | {'Binário':>8} | {'Hexadecimal':>11}")
 
    for ciclo in sorted(dados["ciclo"].unique()):
        bases = converter_bases(int(ciclo)) # int() garante um inteiro Python, e não um tipo do NumPy
        print(f"{bases['decimal']:>8} | {bases['binario']:>8} | {bases['hexadecimal']:>11}")
 
    # Conversão de um valor informado pelo usuário
    entrada = input("\nDigite um número inteiro não negativo para converter: ").strip()
 
    try:
        valor = int(entrada) # Texto que não representa um inteiro gera ValueError
        bases = converter_bases(valor) # Valores negativos também geram ValueError
    except ValueError:
        print("\nValor inválido. Digite um número inteiro igual ou maior que zero.")
        return
 
    print("\nRESULTADO DA CONVERSÃO")
    print("-" * 70)
    print(f"Decimal:..........{bases['decimal']}")
    print(f"Binário:..........{bases['binario']}")
    print(f"Hexadecimal:......{bases['hexadecimal']}")
    print(f"Bits necessários:.{len(bases['binario'])}")
 
    print(
        "\nOs sistemas digitais armazenam valores em binário. O hexadecimal "
        "agrupa 4 bits por dígito e torna códigos de sensores e endereços "
        "mais curtos e legíveis para a equipe."
    )
 
# Cálculo de potência (P = V x I) e resistência equivalente (Lei de Ohm: R = V / I)
def analisar_dados_eletricos(dados):
    limpar_tela()
 
    try:
        eletricos = analisar_dispositivos(dados) # Retorna uma cópia com a coluna potencia_w
    except ValueError as erro:
        print(f"\nErro ao analisar os dados elétricos: {erro}")
        return
 
    unidades = eletricos.attrs["unidades"] # {"tensao_v": "V", "corrente_a": "A", "potencia_w": "W"}
 
    print("=" * 70)
    print("DADOS ELÉTRICOS DOS DISPOSITIVOS - AURORA SIGER")
    print("=" * 70)
 
    # Exemplo de cálculo detalhado com o primeiro registro da base
    exemplo = eletricos.iloc[0]
    tensao = exemplo["tensao_v"]
    corrente = exemplo["corrente_a"]
    potencia = exemplo["potencia_w"]
 
    print("\nEXEMPLO DE CÁLCULO (PRIMEIRO REGISTRO)")
    print("-" * 70)
    print(f"Módulo: {exemplo['modulo']} | Sensor: {exemplo['codigo_sensor']}")
    print(f"Potência:     P = V x I = {tensao:.2f}{unidades['tensao_v']} x "
          f"{corrente:.2f}{unidades['corrente_a']} = {potencia:.2f}{unidades['potencia_w']}")
 
    # Lei de Ohm calculada apenas na apresentação, sem alterar src/dispositivos.py
    if corrente > 0:
        print(f"Lei de Ohm:   R = V / I = {tensao:.2f}V / {corrente:.2f}A = {tensao / corrente:.2f}Ω")
 
    # Médias por módulo, preservando a ordem em que os módulos aparecem no CSV
    resumo = eletricos.groupby("modulo", sort=False).agg(
        tensao_media_v=("tensao_v", "mean"),
        corrente_media_a=("corrente_a", "mean"),
        potencia_media_w=("potencia_w", "mean"),
        potencia_maxima_w=("potencia_w", "max"),
    ).round(2)
 
    print("\nMÉDIAS POR MÓDULO")
    print("-" * 70)
    print(resumo.to_string())
 
    # Registro com maior potência de alimentação
    maior = eletricos.loc[eletricos["potencia_w"].idxmax()]
 
    print("\nMAIOR POTÊNCIA REGISTRADA")
    print("-" * 70)
    print(f"Módulo: {maior['modulo']} | Sensor: {maior['codigo_sensor']} | Ciclo: {maior['ciclo']}")
    print(f"{maior['tensao_v']:.2f}V x {maior['corrente_a']:.2f}A = {maior['potencia_w']:.2f}W "
          f"| Status: {maior['status']}")
 
    print("\nINTERPRETAÇÃO")
    print("-" * 70)
    print(
        "Quedas de tensão ou aumentos de corrente podem indicar sobrecarga "
        "ou falha na alimentação, mas não comprovam sozinhos a causa de uma latência alta."
    )
    print(
        "A potência calculada é a de alimentação do dispositivo (W). Ela não representa "
        "a potência irradiada pela antena nem a energia consumida (Wh)."
    )
 
# Explicação conceitual de dispositivos de entrada e saída do SCIC
def exibir_dispositivos_entrada_saida():
    limpar_tela()
 
    print("=" * 70)
    print("DISPOSITIVOS DE ENTRADA E SAÍDA DO SCIC")
    print("=" * 70)
 
    print("\nENTRADA DE DADOS")
    print("-" * 70)
    print("- Sensores simulados de latência, tensão e corrente (ex.: COM-01, MED-02).")
    print("- Arquivo dados_aurora_siger.csv, que representa as leituras coletadas.")
    print("- Teclado, utilizado pelo operador para navegar no menu e fazer consultas.")
 
    print("\nSAÍDA DE DADOS")
    print("-" * 70)
    print("- Terminal, que exibe tabelas, alertas priorizados e análises.")
    print("- Relatório técnico, que registra resultados e decisões.")
    print("- Em um sistema real: painel de monitoramento ou alarmes para a equipe.")
 
    print("\nINTERFACES DE COMUNICAÇÃO (CONCEITUAIS)")
    print("-" * 70)
    print("- Rede cabeada: enlace principal entre módulos essenciais.")
    print("- Wi-Fi: sensores distribuídos dentro dos módulos.")
    print("- Bluetooth: leitura de curto alcance durante a manutenção.")
    print("- USB: coleta manual de dados ou atualização de dispositivos.")
 
    print("\nCÓDIGOS DE SENSORES EM OUTRAS BASES")
    print("-" * 70)
 
    # Exemplo: número do sensor COM-01 representado nas três bases
    bases = converter_bases(1)
    print(
        f"O número do sensor COM-01 pode ser armazenado como decimal {bases['decimal']}, "
        f"binário {bases['binario'].zfill(8)} ou hexadecimal 0x{bases['hexadecimal'].zfill(2)}."
    )
    print("Internamente, os dispositivos identificam sensores e mensagens em binário.")


# Função de exibiçã oda análise geral do sistema - Menu 8
def exibir_analise_geral(dados):
    if dados is None:
        print("\nNenhum dado está disponível para análise.")
        return
    
    try:
        analise = gerar_analise_final(dados) # src/analise.py

    except ValueError as erro:
        print(f"\nErro ao gerar a análise geral: {erro}")
        return
    
    print("=" * 70)
    print("ANÁLISE GERAL DO SISTEMA - AURORA SIGER")
    print("=" * 70)

    # Resumo
    print("\nRESUMO OPERACIONAL")
    print("-" * 70)

    print(f"Total de Registros: {analise['total_registros']}")

    print("\nRegistros por Status:")

    for status, quantidade in analise["registros_por_status"].items():
        print(f"- {status}: {quantidade}")

    latencia_media = analise["latencia_observada_media_ms"]

    if latencia_media is not None:
        print(f"\nLatência Observada Média:  {latencia_media:.2f}ms")

    print(f"Alertas Priorizados: {analise['total_alertas_priorizados']}")

    # Resumo Elétrico
    print("\nRESUMO ELÉTRICO")
    print("-" * 70)

    resumo_eletrico = analise["resumo_eletrico"]

    potencia_media = resumo_eletrico["potencia_media_w"]
    potencia_maxima = resumo_eletrico["potencia_maxima_w"]

    if potencia_media is not None:
        print(f"Potência Média: {potencia_media:.2f}W")
    
    if potencia_maxima is not None:
        print(f"Potência Máxima: {potencia_maxima:.2f}W")

    # Alertas Urgentes
    print("\nALERTAS MAIS URGENTES")
    print("-" * 70)

    alertas = analise["alertas_mais_urgentes"]

    if len(alertas) == 0:
        print("Nenhum alerta prioritário encontrado.")
    else:
        for posicao, alerta in enumerate(alertas, start=1):
            registro = alerta["registro"]

            print(
                f"\n{posicao}. "
                f"{registro['modulo']} | "
                f"Sensor: {registro['codigo_sensor']} | "
                f"Ciclo: {registro['ciclo']}"
            )

            print(
                f"    Prioridade: {registro['prioridade']} | "
                f"Criticidade: {registro['criticidade']}"
            )

            print(
                f"    Latência Prevista: "
                f"{registro['latencia_prevista_ms']}ms"
            )

            print(
                f"    Latência Observada: "
                f"{registro['latencia_observada_ms']}ms"
            )

            print(
                f"    Justificativa: "
                f"{alerta['justificativa']}"
            )

    # Recomendações
    print("\nRECOMENDAÇÕES OPERACIONAIS")
    print("-" * 70)

    recomendacoes = analise["recomendacoes"]

    if len(recomendacoes) == 0:
        print("Nenhuma recomendação necessária.")

    else:
        for posicao, recomendacao in enumerate(recomendacoes, start=1):
            print(
                f"\n{posicao}. Sensor: "
                f"{recomendacao['codigo_sensor']} | " 
                f"Ciclo: {recomendacao['ciclo']}"
            )

            print(
                f"    Ação Proposta: "
                f"{recomendacao['acao_proposta']}"
            )

            print(
                f"    Justificativa: "
                f"{recomendacao['justificativa']}"
            )

    # Gerenciamento Inteligente
    print("\nGERENCIAMENTO INTELIGENTE DA COMUNICAÇÃO")
    print("-" * 70)

    print(
        "Os sensores simulados fornecem dados como latência, "
        "tensão e corrente para acompanhamento da colônia."
    )

    print(
        "O monitoramento contínuo poderia comparar novas leituras "
        "e identificar recorrências ou condições anormais."
    )

    print(
        "A fila de prioridade com heap apoia a automação da "
        "organização dos atendimentos mais urgentes."
    )

    print(
        "O armazenamento do histórico pode preservar evidências "
        "para inspeção e manutenção."
    )

    print(
        "Enlaces redundantes podem aumentar a disponibilidade "
        "da comunicação em situações críticas."
    )

    print(
        "Uma microrrede poderia ajudar a manter sistemas de "
        "comunicação essenciais, mas exigiria dados adicionais "
        "sobre geração, reserva e consumo de energia."
    )

    print(
        "A base atual não possui histórico suficiente para afirmar "
        "que existe manutenção preditiva treinada."
    )

    # Validação humana
    print("\nVALIDAÇÃO HUMANA")
    print("-" * 70)

    validacao = analise["validacao_humana"]

    if isinstance(validacao, list): # isinstance() para validar se uma variavel ou objeto pertence a determinado tipo de dado ou classe
        for item in validacao:
            print(f"- {item}")
    else:
        print(validacao)

    # Limitações
    print("\nLIMITAÇÕES DO PROTÓTIPO")
    print("-" * 70)

    for limitacao in analise["limitacoes"]:
        print(f"- {limitacao}")

    print("\n" + "=" * 70)
    print("FIM DA ANÁLISE GERAL")
    print("=" * 70)

# Exibindo o menu principal SCIC
def exibir_menu():
    print("\n" + "=" * 60)
    print(" SCIC - SISTEMA DE COMUNICAÇÃO INTERPLANETÁRIA DA COLÔNIA")
    print(" AURORA SIGER")
    print("=" * 60)
    print("1 - Carregar e Visualizar Dados")
    print("2 - Consultar Registros")
    print("3 - Calcular Indicadores e Erros")
    print("4 - Executar Modelo de Previsão")
    print("5 - Analisar Alertas por Prioridade")
    print("6 - Buscar Registros por Prefixo")
    print("7 - Bases Numéricas e Dados Elétricos")
    print("8 - Análise Geral do Sistema")
    print("0 - Encerrar")
    print("=" * 60)

# Mensagem temporária para próxima etapa
def funcionalidade_em_desenvolvimento(nome):
    print(f"\n'{nome}' será implementado nas próximas etapas do projeto.")

# Função principal do sistema que carrega os dados e mantém o menu em execução.
def main():
    dados = carregar_dados() # Carregamento inicial da base

    while True:
        limpar_tela()
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        limpar_tela()

        if opcao == "1":
            dados = carregar_dados(exibir_mensagem=True) # Permite visualizar os registros no .CSV
            if dados is not None:
                visualizar_dados(dados)
                enter()
                limpar_tela()
        elif opcao == "2":
            consultar_registros(dados)
        elif opcao == "3":
            dados = calcular_indicadores_erros(dados)
            enter()
            limpar_tela()
        elif opcao == "4":
            executar_modelo_previsao(dados)
            enter()
            limpar_tela()
        elif opcao == "5":
            analisar_alertas_prioridade(dados)
            enter()
            limpar_tela()
        elif opcao == "6":
            buscar_registros_prefixo(dados)
        elif opcao == "7":
            exibir_bases_eletricidade(dados)
        elif opcao == "8":
            exibir_analise_geral(dados)
            enter()
            limpar_tela()
        elif opcao == "0":
            print("\nSISTEMA ENCERRADO.")
            break
        else:
            print("\nOpção inválida. Digite um número de 0 a 8.")

if __name__ == "__main__":
    main()