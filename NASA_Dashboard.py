# ================================================================================
# ASTEROID DASHBOARD — NASA Small-Body Database
# Dashboard interativo pra explorar dados de asteroides próximos à Terra
# Feito com Streamlit + Plotly + Pandas
# ================================================================================

# ── Importações ──
# pathlib e glob: ferramentas pra navegar pelo sistema de arquivos
# pandas: a biblioteca padrão pra trabalhar com dados em tabela (DataFrame)
# plotly: biblioteca de gráficos interativos (express = gráficos rápidos, graph_objects = controle fino)
# streamlit: o framework que transforma esse script Python em uma web app
from pathlib import Path
import os
import glob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO INICIAL DA PÁGINA
# ────────────────────────────────────────────────────────────────────────────────
# Essa função do Streamlit configura como a aba do navegador vai aparecer.
# Precisa ser a PRIMEIRA chamada do Streamlit no script — se colocar depois,
# dá erro. Layout "wide" faz o conteúdo ocupar a tela inteira, sem margens.
st.set_page_config(
    page_title="☄️ Asteroid Dashboard",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded",  # Sidebar já abre expandida
)


# ────────────────────────────────────────────────────────────────────────────────
# FUNÇÃO: encontrar_arquivo_csv()
# ────────────────────────────────────────────────────────────────────────────────
# Problema clássico: o caminho do arquivo muda dependendo de onde o código roda.
# Essa função resolve isso procurando o CSV automaticamente — primeiro por nome,
# depois por qualquer CSV na pasta, e por último em subpastas (tipo /data).
def encontrar_arquivo_csv():
    """
    Procura por arquivos CSV na pasta atual e subpastas.
    Prioriza arquivos com 'asteroides' ou 'asteroid' no nome.
    Retorna o caminho (Path) do arquivo encontrado, ou None se não achar nada.
    """

    # Pega a pasta onde o script está rodando.
    # O if/else existe porque em alguns ambientes o __file__ não está disponível
    # (como em notebooks Jupyter), então a gente cai pro diretório atual (cwd).
    if '__file__' in globals():
        pasta_atual = Path(__file__).resolve().parent
    else:
        pasta_atual = Path.cwd()

    # Lista de nomes de arquivo que o CSV pode ter — os mais comuns primeiro
    possiveis_nomes = [
        "asteroides.csv",
        "asteroides 2025.csv",
        "asteroids.csv",
        "asteroides_perigosos.csv",
        "dados_asteroides.csv",
        "asteroides_2025.csv",
        "asteroid_data.csv",
        "nea.csv"
    ]

    # Tentativa 1: procura pelo nome exato na pasta do script
    for nome in possiveis_nomes:
        caminho = pasta_atual / nome
        if caminho.exists():
            st.sidebar.success(f"✅ Arquivo encontrado: {nome}")
            return caminho

    # Tentativa 2: pega qualquer CSV na pasta, priorizando os que têm
    # palavras-chave relacionadas a asteroides no nome
    arquivos_csv = list(pasta_atual.glob("*.csv"))

    if arquivos_csv:
        arquivos_asteroides = [
            f for f in arquivos_csv
            if any(keyword in f.stem.lower() for keyword in ['asteroide', 'asteroid', 'nea', 'pha'])
        ]

        if arquivos_asteroides:
            st.sidebar.success(f"✅ Arquivo encontrado: {arquivos_asteroides[0].name}")
            return arquivos_asteroides[0]

        # Se não teve match com as palavras-chave, pega o primeiro CSV que encontrar
        st.sidebar.success(f"✅ Arquivo encontrado: {arquivos_csv[0].name}")
        return arquivos_csv[0]

    # Tentativa 3 (último recurso): procura dentro de subpastas
    for subpasta in pasta_atual.glob("*/"):
        arquivos_csv = list(subpasta.glob("*.csv"))
        if arquivos_csv:
            arquivos_asteroides = [
                f for f in arquivos_csv
                if any(keyword in f.stem.lower() for keyword in ['asteroide', 'asteroid', 'nea', 'pha'])
            ]
            if arquivos_asteroides:
                st.sidebar.success(f"✅ Arquivo encontrado: {arquivos_asteroides[0].name} (em subpasta)")
                return arquivos_asteroides[0]

            st.sidebar.success(f"✅ Arquivo encontrado: {arquivos_csv[0].name} (em subpasta)")
            return arquivos_csv[0]

    # Se chegou até aqui, não encontrou nada
    return None


# ────────────────────────────────────────────────────────────────────────────────
# CSS CUSTOMIZADO — TEMA ESPACIAL
# ────────────────────────────────────────────────────────────────────────────────
# O st.markdown com unsafe_allow_html=True permite injetar HTML/CSS puro na página.
# Aqui a gente sobrescreve os estilos padrão do Streamlit pra criar o tema espacial:
# fundo escuro degradê, fontes futuristas (Orbitron + Exo 2), cards com brilho roxa.
st.markdown(
    """
    <style>
        /* Importa as fontes do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

        /* Fundo geral — degradê radial que imita o espaço (roxo escuro → preto) */
        .stApp {
            background: radial-gradient(ellipse at 20% 10%, #0d0d2b 0%, #050510 60%, #000000 100%);
            font-family: 'Exo 2', sans-serif;
        }

        /* Títulos h1 com a fonte espacial Orbitron */
        h1 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 3px;
        }

        h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 1px;
        }

        /* Cards de KPI (st.metric) — fundo degradê azul-roxo com borda roxa translúcida.
           O :hover adiciona um efeito de brilho quando passa o mouse */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(30,10,80,0.85) 0%, rgba(10,30,80,0.85) 100%);
            border: 1px solid rgba(130,80,255,0.45);
            border-radius: 14px;
            padding: 18px 22px;
            box-shadow: 0 0 22px rgba(100,60,255,0.25), inset 0 0 8px rgba(100,60,255,0.08);
            transition: box-shadow 0.3s;
        }

        [data-testid="metric-container"]:hover {
            box-shadow: 0 0 38px rgba(100,60,255,0.5);
        }

        /* Estilos do label, valor e delta dos cards de KPI */
        [data-testid="stMetricLabel"] {
            color: #a78bfa !important;
            font-size: 0.78rem;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            color: #e0d7ff !important;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.6rem;
        }

        [data-testid="stMetricDelta"] {
            color: #7dd3fc !important;
        }

        /* Sidebar (barra lateral) com gradiente escuro e borda roxa sutil */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a20 0%, #05050f 100%);
            border-right: 1px solid rgba(130,80,255,0.3);
        }

        [data-testid="stSidebar"] * {
            color: #c4b5fd !important;
        }

        /* Linhas divisórias (st.markdown("---")) */
        hr {
            border-color: rgba(130,80,255,0.25) !important;
        }

        /* Expanders — aquelas caixinhas que abrem/fecham ao clicar */
        .streamlit-expanderHeader {
            background: rgba(30,10,80,0.6) !important;
            border: 1px solid rgba(130,80,255,0.3) !important;
            border-radius: 8px !important;
            color: #c4b5fd !important;
            font-family: 'Exo 2', sans-serif;
        }

        /* Tabelas de dados (st.dataframe) */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(130,80,255,0.3) !important;
            border-radius: 10px;
        }

        /* Cards de insight — usados na seção de análises automáticas.
           Borda esquerda grossa roxa pra destacar o conteúdo */
        .insight-card {
            background: linear-gradient(135deg, rgba(20,5,60,0.9), rgba(5,20,60,0.9));
            border: 1px solid rgba(130,80,255,0.5);
            border-left: 4px solid #7c3aed;
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 10px;
            color: #ddd6fe;
            font-size: 0.95rem;
        }

        /* Título principal com texto em gradiente (efeito de cor que muda).
           O -webkit-background-clip: text faz o gradiente ser aplicado só no texto */
        .star-header {
            text-align: center;
            padding: 6px 0 20px;
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
        }

        /* Subtítulo abaixo do título principal */
        .sub-header {
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            letter-spacing: 2px;
            margin-top: -16px;
            margin-bottom: 28px;
        }

        /* Alerta de erro quando não encontra o arquivo CSV */
        .file-alert {
            background: linear-gradient(135deg, rgba(80,20,20,0.9), rgba(40,10,10,0.9));
            border: 1px solid rgba(255,80,80,0.5);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ────────────────────────────────────────────────────────────────────────────────
# PALETA DE CORES E TEMPLATE DO PLOTLY
# ────────────────────────────────────────────────────────────────────────────────
# Centralizar as cores num dicionário é uma boa prática:
# se precisar mudar uma cor, muda só aqui e reflete em todos os gráficos.
CORES = {
    "roxo":       "#7c3aed",
    "roxo_claro": "#a78bfa",
    "azul":       "#3b82f6",
    "azul_claro": "#7dd3fc",
    "rosa":       "#ec4899",
    "verde":      "#34d399",
    "amarelo":    "#fbbf24",
    "fundo":      "#050510",
    "texto":      "#e0d7ff",
}

# Template do Plotly — aplicado em todos os gráficos pra garantir consistência visual.
# Fundo transparente deixa o gráfico "flutuar" sobre o fundo escuro da página.
# As gridlines são roxas e bem sutis pra não poluir.
PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",           # Fundo externo do gráfico: transparente
        plot_bgcolor="rgba(10,5,30,0.6)",        # Fundo interno (área do plot): roxo escuro translúcido
        font=dict(color=CORES["texto"], family="Exo 2, sans-serif"),
        xaxis=dict(gridcolor="rgba(130,80,255,0.12)", zerolinecolor="rgba(130,80,255,0.2)"),
        yaxis=dict(gridcolor="rgba(130,80,255,0.12)", zerolinecolor="rgba(130,80,255,0.2)"),
        # Sequência de cores padrão pra séries de dados
        colorway=[
            CORES["roxo_claro"], CORES["azul_claro"], CORES["rosa"],
            CORES["verde"], CORES["amarelo"], CORES["azul"], CORES["roxo"]
        ],
    )
)


# ────────────────────────────────────────────────────────────────────────────────
# FUNÇÃO: carregar_dados()
# ────────────────────────────────────────────────────────────────────────────────
# O decorador @st.cache_data é fundamental aqui:
# sem ele, o Streamlit recarregaria o CSV do zero toda vez que o usuário mexesse
# em qualquer filtro. Com ele, o resultado fica em cache e só recarrega quando
# o argumento da função muda (ou seja, quando muda o arquivo).
@st.cache_data(show_spinner="🌌 Carregando dados do cinturão de asteroides…")
def carregar_dados(caminho_especifico=None) -> pd.DataFrame:
    """
    Lê o CSV de asteroides e retorna um DataFrame já tratado.
    Se caminho_especifico for passado (upload manual), usa ele.
    Caso contrário, chama encontrar_arquivo_csv() pra achar automaticamente.
    """

    if caminho_especifico:
        # O usuário fez upload de um arquivo manualmente via st.file_uploader
        df = pd.read_csv(caminho_especifico)
    else:
        csv_path = encontrar_arquivo_csv()

        if csv_path is None:
            # Não achou nenhum CSV — mostra um erro formatado e para a execução
            st.error("""
                <div class="file-alert">
                    <h3>❌ Arquivo CSV não encontrado!</h3>
                    <p>Não foi possível encontrar nenhum arquivo CSV na pasta atual ou subpastas.</p>
                    <p>Por favor, verifique se:</p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>O arquivo CSV está na mesma pasta que este script</li>
                        <li>O arquivo tem extensão .csv</li>
                        <li>O arquivo contém dados de asteroides</li>
                    </ul>
                    <br>
                    <p><b>Nomes esperados:</b> asteroides.csv, asteroids.csv, asteroides 2025.csv, etc.</p>
                    <p>💡 <b>Dica:</b> Use o seletor abaixo para fazer upload do arquivo manualmente.</p>
                </div>
            """, unsafe_allow_html=True)
            return None

        df = pd.read_csv(csv_path)

        # Mostra no sidebar o nome e tamanho do arquivo carregado
        tamanho_mb = csv_path.stat().st_size / (1024 * 1024)
        st.sidebar.info(f"📄 Arquivo: {csv_path.name} ({tamanho_mb:.1f} MB)")

    # ── Tratamento das colunas numéricas ──
    # pd.to_numeric com errors="coerce" tenta converter pra número;
    # se não conseguir (ex: valor "N/A" ou string), coloca NaN em vez de dar erro.
    for col in ["moid_au", "per_y", "H", "diameter_km", "albedo", "e"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Preenche valores nulos da coluna de classe com "Desconhecida"
    if "class" in df.columns:
        df["class"] = df["class"].fillna("Desconhecida")

    # ── Normalização da coluna PHA (Potentially Hazardous Asteroid) ──
    # Essa coluna pode vir em formatos diferentes dependendo da fonte:
    # "TRUE"/"FALSE", "Y"/"N", 1/0, True/False. A gente padroniza pra booleano.
    if "pha" in df.columns:
        if df["pha"].dtype == "object":
            # Se for string, verifica se é alguma representação de "verdadeiro"
            df["pha"] = df["pha"].astype(str).str.upper().isin(["TRUE", "T", "1", "YES", "Y"])
        elif df["pha"].dtype in ["int64", "float64"]:
            df["pha"] = df["pha"].astype(bool)
        else:
            df["pha"] = df["pha"].astype(bool)
    else:
        # Se a coluna não existe, cria ela com False pra não dar KeyError depois
        df["pha"] = False

    # Mesma lógica pra coluna de diâmetro estimado
    if "diameter_is_estimated" in df.columns:
        df["diameter_is_estimated"] = df["diameter_is_estimated"].astype(bool)
    else:
        df["diameter_is_estimated"] = False

    return df


# ────────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS (parte 1: upload de arquivo)
# ────────────────────────────────────────────────────────────────────────────────
# O "with st.sidebar:" agrupa todos os componentes dentro da barra lateral.
# Primeiro criamos só o uploader, porque os outros filtros dependem dos dados
# estarem carregados (precisamos saber quais classes existem, min/max dos valores, etc.)
with st.sidebar:
    st.markdown("## 🛰️ Filtros")
    st.markdown("---")

    st.subheader("📁 Dados")

    # Widget de upload — aceita só arquivos .csv
    uploaded_file = st.file_uploader(
        "Ou faça upload do CSV (opcional):",
        type=["csv"],
        help="Faça upload de um arquivo CSV diferente"
    )

    st.markdown("---")


# ────────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ────────────────────────────────────────────────────────────────────────────────
# Define qual fonte de dados usar e carrega o DataFrame.
# st.stop() é um jeito elegante de parar a execução do script —
# tudo que vem depois dele não roda. Útil quando não tem dados pra exibir.
if uploaded_file is not None:
    df_raw = carregar_dados(uploaded_file)
    st.sidebar.success(f"✅ Usando arquivo enviado: {uploaded_file.name}")
else:
    df_raw = carregar_dados()

# Sem dados = sem dashboard
if df_raw is None:
    st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS (parte 2: filtros dinâmicos baseados nos dados)
# ────────────────────────────────────────────────────────────────────────────────
# Agora que o df_raw está carregado, podemos criar filtros com os valores reais.
with st.sidebar:

    # ── Filtro de Classe Orbital ──
    # multiselect permite selecionar várias opções ao mesmo tempo.
    # Por padrão deixa todas selecionadas.
    if "class" in df_raw.columns:
        classes_disp = sorted(df_raw["class"].unique().tolist())
        classes_sel = st.multiselect(
            "🪐 Classe Orbital",
            options=classes_disp,
            default=classes_disp,
            help="Selecione as classes orbitais a exibir",
        )
    else:
        classes_sel = []

    # ── Filtro de PHA ──
    # radio button porque são opções mutuamente exclusivas (só pode escolher uma)
    pha_opcao = st.radio(
        "⚠️ Potencialmente Perigoso (PHA)",
        options=["Todos", "Somente perigosos", "Somente não-perigosos"],
        index=0,
    )

    # ── Filtro de Diâmetro ──
    # slider de intervalo — o usuário arrasta dois pontos pra definir min e max.
    # dropna() remove os NaN antes de calcular min/max pra não dar erro.
    if "diameter_km" in df_raw.columns and df_raw["diameter_km"].notna().any():
        diam_min_val = float(df_raw["diameter_km"].dropna().min())
        diam_max_val = float(df_raw["diameter_km"].dropna().max())
        diam_range = st.slider(
            "📏 Diâmetro (km)",
            min_value=diam_min_val,
            max_value=diam_max_val,
            value=(diam_min_val, diam_max_val),
            step=0.1,
        )
    else:
        diam_range = (0, 100)

    # ── Filtro de Magnitude Absoluta (H) ──
    # H é o brilho intrínseco do asteroide: quanto menor o H, maior/mais brilhante o objeto.
    if "H" in df_raw.columns and df_raw["H"].notna().any():
        h_min_val = float(df_raw["H"].dropna().min())
        h_max_val = float(df_raw["H"].dropna().max())
        h_range = st.slider(
            "💡 Magnitude Absoluta (H)",
            min_value=h_min_val,
            max_value=h_max_val,
            value=(h_min_val, h_max_val),
            step=0.5,
            help="Menor H = objeto mais brilhante/maior",
        )
    else:
        h_range = (0, 30)

    st.markdown("---")
    st.markdown(
        "<small style='color:#475569'>Dados: NASA JPL Small-Body Database</small>",
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────────
# APLICAÇÃO DOS FILTROS
# ────────────────────────────────────────────────────────────────────────────────
# Cria uma cópia do DataFrame original e vai filtrando conforme as seleções do usuário.
# Usar .copy() é importante pra não modificar o df_raw cacheado.
df = df_raw.copy()

# Filtro por classe orbital
if classes_sel:
    df = df[df["class"].isin(classes_sel)]

# Filtro por PHA
if pha_opcao == "Somente perigosos":
    df = df[df["pha"] == True]
elif pha_opcao == "Somente não-perigosos":
    df = df[df["pha"] == False]

# Filtro por diâmetro — mantém os NaN com .isna() pra não descartar asteroides
# sem medição de diâmetro (que são a maioria)
if "diameter_km" in df.columns:
    mask_diam = df["diameter_km"].isna() | (
        (df["diameter_km"] >= diam_range[0]) & (df["diameter_km"] <= diam_range[1])
    )
    df = df[mask_diam]

# Filtro por magnitude H (mesma lógica: mantém os NaN)
if "H" in df.columns:
    mask_h = df["H"].isna() | ((df["H"] >= h_range[0]) & (df["H"] <= h_range[1]))
    df = df[mask_h]

# Salva o total de registros após filtros — usado em todos os cálculos de %
total = len(df)


# ────────────────────────────────────────────────────────────────────────────────
# CABEÇALHO DO DASHBOARD
# ────────────────────────────────────────────────────────────────────────────────
# Renderiza o título principal com a classe CSS "star-header" (gradiente colorido)
# e o subtítulo com "sub-header". O unsafe_allow_html=True é necessário pra isso.
st.markdown('<div class="star-header">☄️ ASTEROID DASHBOARD</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">ANÁLISE EXPLORATÓRIA · NASA SMALL-BODY DATABASE</div>',
    unsafe_allow_html=True,
)


# ────────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ────────────────────────────────────────────────────────────────────────────────

def pct(cond: pd.Series, total: int) -> float:
    """
    Calcula a porcentagem de linhas onde a condição é True.
    Exemplo: pct(df['pha'] == True, total) → 5.3
    O 'if total' evita divisão por zero quando o DataFrame está vazio.
    """
    return round((cond.sum() / total) * 100, 2) if total else 0.0


def fmt_num(n: int | float) -> str:
    """
    Formata um número com ponto como separador de milhar (padrão BR).
    Exemplo: fmt_num(1234567) → "1.234.567"
    O f"{int(n):,}" já faz a formatação com vírgula, e depois a gente troca por ponto.
    """
    return f"{int(n):,}".replace(",", ".")


# ────────────────────────────────────────────────────────────────────────────────
# CARDS DE KPI (Key Performance Indicators)
# ────────────────────────────────────────────────────────────────────────────────
# st.columns(5) cria 5 colunas de largura igual lado a lado.
# st.metric() renderiza aquele card com título, valor grande e delta embaixo.
# O "delta" é o textinho menor embaixo do valor principal.
st.markdown("### 🔭 Indicadores Principais")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("☄️ Total de Asteroides", fmt_num(total) if total > 0 else "0")

if total > 0:
    # % de asteroides classificados como Potencialmente Perigosos
    k2.metric(
        "⚠️ Perigosos (PHA)",
        f"{pct(df['pha'] == True, total):.1f}%" if 'pha' in df.columns else "N/A",
        delta=f"{(df['pha'] == True).sum()} objetos" if 'pha' in df.columns else "",
    )

    # MOID = Minimum Orbit Intersection Distance
    # É a menor distância possível entre as órbitas da Terra e do asteroide.
    # Abaixo de 0.05 AU é considerado próximo (dentro da zona de monitoramento).
    if 'moid_au' in df.columns:
        k3.metric(
            "🌍 Próximos da Terra",
            f"{pct(df['moid_au'] < 0.05, total):.1f}%",
            delta="MOID < 0.05 AU",
        )
    else:
        k3.metric("🌍 Próximos da Terra", "N/A", delta="")

    # per_y = período orbital em anos. < 2 anos = órbita bem rápida
    if 'per_y' in df.columns:
        k4.metric(
            "⚡ Órbita Rápida",
            f"{pct(df['per_y'] < 2, total):.1f}%",
            delta="período < 2 anos",
        )
    else:
        k4.metric("⚡ Órbita Rápida", "N/A", delta="")

    # > 1 km é considerado "grande" na classificação de asteroides
    if 'diameter_km' in df.columns:
        k5.metric(
            "🔵 Grandes (> 1 km)",
            f"{pct(df['diameter_km'] > 1, total):.1f}%",
            delta=f"{(df['diameter_km'] > 1).sum()} objetos",
        )
    else:
        k5.metric("🔵 Grandes (> 1 km)", "N/A", delta="")
else:
    # Se não tem dados (filtros muito restritivos), mostra tudo zerado
    k2.metric("⚠️ Perigosos (PHA)", "0%")
    k3.metric("🌍 Próximos da Terra", "0%")
    k4.metric("⚡ Órbita Rápida", "0%")
    k5.metric("🔵 Grandes (> 1 km)", "0%")

st.markdown("---")

# Aviso e parada se os filtros zeraram os dados
if total == 0:
    st.warning("⚠️ Nenhum asteroide encontrado com os filtros selecionados. Ajuste os filtros para visualizar os dados.")
    st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# GRÁFICOS — LINHA 1: Resumo percentual + Pizza de classes
# ────────────────────────────────────────────────────────────────────────────────
# st.columns([3, 2]) cria duas colunas com proporção 3:2 (a primeira maior)
col_bar, col_pie = st.columns([3, 2])

# ── Gráfico de barras horizontais ──
# Mostra várias categorias e o percentual de asteroides que se encaixam em cada uma.
with col_bar:
    st.markdown("#### 📊 Resumo Percentual")

    # Monta dinamicamente a lista de categorias — só inclui as que têm coluna no CSV
    categorias = []

    if "name" in df.columns:
        categorias.append(("Com nome", df["name"].notna() & (df["name"] != "")))
    if "pha" in df.columns:
        categorias.append(("Perigosos (PHA)", df["pha"] == True))
    if "moid_au" in df.columns:
        categorias.append(("Próx. Terra (MOID<0.05)", df["moid_au"] < 0.05))
    if "per_y" in df.columns:
        categorias.append(("Órbita rápida (<2 anos)", df["per_y"] < 2))
    if "H" in df.columns:
        categorias.append(("Alta luminosidade (H<15)", df["H"] < 15))
    if "e" in df.columns:
        categorias.append(("Órbita alongada (e>0.5)", df["e"] > 0.5))
    if "albedo" in df.columns:
        categorias.append(("Alto albedo (>0.25)", df["albedo"] > 0.25))
    if "diameter_is_estimated" in df.columns:
        categorias.append(("Diâm. estimado", df["diameter_is_estimated"] == True))
    if "diameter_km" in df.columns:
        categorias.append(("Grandes (>1 km)", df["diameter_km"] > 1))

    # Constrói o DataFrame do resumo e ordena pelo percentual
    resumo = pd.DataFrame(
        {
            "Categoria": [cat[0] for cat in categorias],
            "Percentual": [pct(cat[1], total) for cat in categorias],
        }
    ).sort_values("Percentual", ascending=True)

    if len(resumo) > 0:
        # go.Bar com orientation="h" = barras na horizontal
        # O colorscale faz as barras mais escuras ou claras conforme o valor
        fig_bar = go.Figure(
            go.Bar(
                x=resumo["Percentual"],
                y=resumo["Categoria"],
                orientation="h",
                marker=dict(
                    color=resumo["Percentual"],
                    colorscale=[[0, "#3730a3"], [0.5, "#7c3aed"], [1, "#c084fc"]],
                    line=dict(color="rgba(200,150,255,0.4)", width=0.8),
                ),
                text=[f"{v:.1f}%" for v in resumo["Percentual"]],
                textposition="outside",
                textfont=dict(color="#e0d7ff", size=11),
            )
        )

        fig_bar.update_layout(
            **PLOTLY_TEMPLATE["layout"].to_plotly_json(),  # Aplica o template global
            height=380,
            margin=dict(l=10, r=60, t=10, b=10),
            xaxis_title="% do total",
            yaxis_title="",
            bargap=0.25,
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Não há dados suficientes para gerar o resumo percentual.")


# ── Gráfico de rosca (donut chart) ──
# Mostra a distribuição das classes orbitais.
# hole=0.48 cria o buraco no meio, transformando a pizza em rosca.
with col_pie:
    st.markdown("#### 🪐 Distribuição por Classe")

    if "class" in df.columns:
        # Pega as 10 classes mais frequentes (top 10) pra não poluir o gráfico
        df_cls = (
            df["class"].value_counts().reset_index()
            .rename(columns={"class": "Classe", "count": "Qtd"})
            .head(10)
        )

        fig_pie = go.Figure(
            go.Pie(
                labels=df_cls["Classe"],
                values=df_cls["Qtd"],
                hole=0.48,
                marker=dict(
                    colors=[
                        "#7c3aed", "#6d28d9", "#4f46e5", "#3b82f6", "#0ea5e9",
                        "#06b6d4", "#14b8a6", "#10b981", "#a78bfa", "#c084fc",
                    ],
                    line=dict(color="#050510", width=1.5),
                ),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e0d7ff"),
                # hovertemplate define o que aparece ao passar o mouse em cada fatia
                hovertemplate="<b>%{label}</b><br>%{value:,} asteroides<br>%{percent}<extra></extra>",
            )
        )

        fig_pie.update_layout(
            **PLOTLY_TEMPLATE["layout"].to_plotly_json(),
            height=380,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            # annotations coloca o total no centro da rosca
            annotations=[
                dict(
                    text=f"<b>{fmt_num(total)}</b><br><span style='font-size:10px'>total</span>",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="#e0d7ff"),
                )
            ],
        )

        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Coluna 'class' não encontrada nos dados.")


# ────────────────────────────────────────────────────────────────────────────────
# GRÁFICOS — LINHA 2: Distribuição por tamanho + Scatter MOID vs Diâmetro
# ────────────────────────────────────────────────────────────────────────────────
# Proporção [1, 2] = primeira coluna ocupa 1/3, segunda ocupa 2/3 da largura
col_tam, col_scatter = st.columns([1, 2])

# ── Gráfico de barras verticais: distribuição por tamanho ──
with col_tam:
    st.markdown("#### 📏 Distribuição por Tamanho")

    if "diameter_km" in df.columns:
        # Classifica os asteroides em 3 categorias de tamanho
        df_tam = pd.DataFrame(
            {
                "Categoria": ["Pequenos\n(<100m)", "Médios\n(100m–1km)", "Grandes\n(>1km)"],
                "Percentual": [
                    pct(df["diameter_km"] < 0.1, total),
                    pct((df["diameter_km"] >= 0.1) & (df["diameter_km"] <= 1), total),
                    pct(df["diameter_km"] > 1, total),
                ],
                "Cor": [CORES["azul_claro"], CORES["roxo_claro"], CORES["rosa"]],
            }
        )

        fig_tam = go.Figure(
            go.Bar(
                x=df_tam["Categoria"],
                y=df_tam["Percentual"],
                marker_color=df_tam["Cor"],
                marker_line=dict(color="rgba(255,255,255,0.1)", width=0.5),
                text=[f"{v:.1f}%" for v in df_tam["Percentual"]],
                textposition="outside",
                textfont=dict(color="#e0d7ff", size=12),
            )
        )

        fig_tam.update_layout(
            **PLOTLY_TEMPLATE["layout"].to_plotly_json(),
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="% do total",
            xaxis_title="",
            bargap=0.35,
        )

        st.plotly_chart(fig_tam, use_container_width=True)
    else:
        st.info("Coluna 'diameter_km' não encontrada nos dados.")


# ── Scatter plot: MOID vs Diâmetro ──
# Cada ponto = um asteroide. Eixo X = distância mínima à Terra, Eixo Y = tamanho.
# A ideia é ver se os asteroides grandes também são os que chegam mais perto.
with col_scatter:
    st.markdown("#### 🌌 MOID vs Diâmetro (proximidade à Terra)")

    if "moid_au" in df.columns and "diameter_km" in df.columns:
        # Filtra só os registros que têm as duas colunas preenchidas
        df_sc = df[df["moid_au"].notna() & df["diameter_km"].notna()].copy()

        # Cria coluna de label pra colorir os pontos conforme o status PHA
        if "pha" in df.columns:
            df_sc["PHA_label"] = df_sc["pha"].map({True: "⚠️ Perigoso", False: "✅ Seguro"})
        else:
            df_sc["PHA_label"] = "Desconhecido"

        # .sample(min(3000, len(df_sc))) pega uma amostra aleatória de até 3000 pontos.
        # Isso é necessário pra não travar o browser com dezenas de milhares de pontos.
        # random_state=42 garante que a amostra seja sempre a mesma (reprodutível).
        fig_sc = px.scatter(
            df_sc.sample(min(3000, len(df_sc)), random_state=42),
            x="moid_au",
            y="diameter_km",
            color="PHA_label",
            color_discrete_map={"⚠️ Perigoso": CORES["rosa"], "✅ Seguro": CORES["azul_claro"]},
            opacity=0.65,
            hover_data={"moid_au": ":.4f", "diameter_km": ":.2f"},
            labels={"moid_au": "MOID (AU)", "diameter_km": "Diâmetro (km)", "PHA_label": "Tipo"},
            log_y=True,  # Escala logarítmica no Y porque os tamanhos variam em várias ordens de grandeza
        )

        fig_sc.update_traces(marker=dict(size=5, line=dict(width=0.4, color="rgba(255,255,255,0.3)")))

        # Linha vertical tracejada marcando o limite de 0.05 AU (definição de NEO próximo)
        fig_sc.add_vline(
            x=0.05,
            line_dash="dash",
            line_color=CORES["amarelo"],
            annotation_text="Limite NEO (0.05 AU)",
            annotation_font_color=CORES["amarelo"],
        )

        fig_sc.update_layout(
            **PLOTLY_TEMPLATE["layout"].to_plotly_json(),
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.18, font=dict(size=11)),
        )

        st.plotly_chart(fig_sc, use_container_width=True)
    else:
        st.info("Colunas 'moid_au' ou 'diameter_km' não encontradas nos dados.")


# ────────────────────────────────────────────────────────────────────────────────
# GRÁFICOS — LINHA 3: H vs Diâmetro + Boxplot de excentricidade
# ────────────────────────────────────────────────────────────────────────────────
col_hd, col_e = st.columns(2)

# ── Scatter: Magnitude Absoluta (H) vs Diâmetro ──
# Existe uma relação física entre H e o tamanho do asteroide:
# quanto menor o H, maior o objeto. Esse gráfico visualiza essa correlação.
with col_hd:
    st.markdown("#### 💡 Magnitude Absoluta (H) vs Diâmetro")

    if "H" in df.columns and "diameter_km" in df.columns:
        df_hd = df[df["H"].notna() & df["diameter_km"].notna()].copy()

        if len(df_hd) > 0:
            # Se tiver a coluna de classe, colore os pontos por ela
            color_col = "class" if "class" in df.columns else None

            fig_hd = px.scatter(
                df_hd.sample(min(3000, len(df_hd)), random_state=7),
                x="H",
                y="diameter_km",
                color=color_col,
                opacity=0.55,
                log_y=True,
                labels={"H": "Magnitude Absoluta (H)", "diameter_km": "Diâmetro (km)"},
            )

            fig_hd.update_traces(marker=dict(size=4))

            fig_hd.update_layout(
                **PLOTLY_TEMPLATE["layout"].to_plotly_json(),
                height=330,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
            )

            st.plotly_chart(fig_hd, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico.")
    else:
        st.info("Colunas 'H' ou 'diameter_km' não encontradas nos dados.")


# ── Boxplot: Excentricidade por classe orbital ──
# Excentricidade (e) descreve o formato da órbita:
#   e = 0 → órbita perfeitamente circular
#   0 < e < 1 → elipse (a maioria dos asteroides)
#   e = 1 → parábola (objeto em trajetória de escape)
# O boxplot mostra a distribuição da excentricidade dentro de cada classe.
with col_e:
    st.markdown("#### 🌀 Excentricidade Orbital por Classe")

    if "e" in df.columns and "class" in df.columns:
        df_e = df[df["e"].notna() & df["class"].notna()].copy()

        # Pega as 8 classes mais frequentes pra não poluir o gráfico
        top_classes = df_e["class"].value_counts().head(8).index
        df_e = df_e[df_e["class"].isin(top_classes)]

        if len(df_e) > 0:
            fig_e = px.box(
                df_e,
                x="class",
                y="e",
                color="class",
                labels={"class": "Classe Orbital", "e": "Excentricidade"},
                color_discrete_sequence=[
                    CORES["roxo"], CORES["azul"], CORES["rosa"], CORES["verde"],
                    CORES["amarelo"], CORES["azul_claro"], CORES["roxo_claro"], CORES["texto"],
                ],
            )

            # Linha horizontal tracejada em e=1 (limite teórico da órbita parabólica)
            fig_e.add_hline(
                y=1.0,
                line_dash="dot",
                line_color=CORES["rosa"],
                annotation_text="e=1 (parabólica)",
                annotation_font_color=CORES["rosa"],
            )

            fig_e.update_layout(
                **PLOTLY_TEMPLATE["layout"].to_plotly_json(),
                height=330,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
            )

            st.plotly_chart(fig_e, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico.")
    else:
        st.info("Colunas 'e' ou 'class' não encontradas nos dados.")


# ────────────────────────────────────────────────────────────────────────────────
# INSIGHTS AUTOMÁTICOS
# ────────────────────────────────────────────────────────────────────────────────
# Essa seção analisa os dados filtrados e gera observações textuais automáticas.
# A lógica é simples: calcula métricas e, dependendo do valor, escolhe uma mensagem.
# Os textos aparecem nos cards com a classe CSS "insight-card".
st.markdown("---")
st.markdown("### 🤖 Insights Automáticos")

insights = []

if total > 0:

    # ── Insight 1: proporção de PHAs ──
    if "pha" in df.columns:
        pct_pha = pct(df["pha"] == True, total)
        if pct_pha > 5:
            # Acima de 5% = alerta de risco elevado
            insights.append(
                f"🚨 <b>{pct_pha:.1f}%</b> dos asteroides filtrados são classificados como "
                "Potencialmente Perigosos (PHA) — acima do limiar de atenção de 5%."
            )
        elif pct_pha > 0:
            insights.append(
                f"✅ Apenas <b>{pct_pha:.1f}%</b> dos asteroides filtrados são Potencialmente "
                "Perigosos (PHA). O risco imediato é baixo dentro desta seleção."
            )

    # ── Insight 2: asteroides com MOID < 0.05 AU ──
    if "moid_au" in df.columns:
        pct_moid = pct(df["moid_au"] < 0.05, total)
        insights.append(
            f"🌍 <b>{pct_moid:.1f}%</b> dos asteroides têm MOID inferior a 0.05 AU, "
            "passando dentro da zona de monitoramento próxima à Terra."
        )

    # ── Insight 3: classe orbital mais comum ──
    if "class" in df.columns and total > 0:
        classe_dom = df["class"].value_counts().idxmax() if total > 0 else "N/A"
        pct_cls = pct(df["class"] == classe_dom, total)
        insights.append(
            f"🪐 A classe orbital dominante é <b>{classe_dom}</b>, representando "
            f"<b>{pct_cls:.1f}%</b> dos asteroides nesta seleção."
        )

    # ── Insight 4: asteroides grandes ──
    if "diameter_km" in df.columns:
        pct_grandes = pct(df["diameter_km"] > 1, total)
        if pct_grandes > 10:
            insights.append(
                f"☄️ <b>{pct_grandes:.1f}%</b> dos asteroides têm diâmetro superior a 1 km — "
                "um número relevante de objetos de grande porte."
            )

    # ── Insight 5: magnitude típica ──
    if "H" in df.columns and df["H"].notna().any():
        mediana_h = df["H"].median()
        if mediana_h is not None:
            insights.append(
                f"💡 A mediana de magnitude absoluta (H) é <b>{mediana_h:.1f}</b>. "
                "Isso indica o brilho típico dos asteroides neste conjunto."
            )

# Renderiza cada insight como um card HTML estilizado
for insight in insights:
    st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
