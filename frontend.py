import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Explorador Star Wars", page_icon="⚔️", layout="wide")

st.title("🌌 Explorador Star Wars")
st.markdown("Explore o universo da saga consumindo nossa **API Serverless**.")

if 'page' not in st.session_state:
    st.session_state.page = 1
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = None

st.sidebar.header("Filtros de Busca")

mapa_categorias = {
    "Personagens": "people",
    "Planetas": "planets",
    "Naves": "starships",
    "Filmes": "films"
}

categoria_visual = st.sidebar.selectbox(
    "Escolha uma Categoria:",
    options=list(mapa_categorias.keys()),
    index=0
)
category_api = mapa_categorias[categoria_visual]

search_term = st.sidebar.text_input("Buscar por nome (opcional):", "")

def reset_page():
    st.session_state.page = 1

btn_buscar = st.sidebar.button("Buscar Dados 🔎", on_click=reset_page)

def fetch_data(cat, term, pg):
    api_url = "http://localhost:8080/"
    params = {
        "category": cat,
        "search": term,
        "page": pg
    }
    try:
        return requests.get(api_url, params=params)
    except requests.exceptions.ConnectionError:
        return None

if btn_buscar or st.session_state.data_cache is not None:
    
    
    if btn_buscar:
        st.session_state.last_category = category_api
        st.session_state.last_search = search_term

    
    cat_to_use = st.session_state.get('last_category', category_api)
    search_to_use = st.session_state.get('last_search', search_term)

    with st.spinner(f'Carregando página {st.session_state.page}...'):
        response = fetch_data(cat_to_use, search_to_use, st.session_state.page)

        if response and response.status_code == 200:
            data = response.json()
            st.session_state.data_cache = data 
            
            results = data.get("data", {}).get("results", [])
            count = data.get("data", {}).get("count", 0)
            
            
            api_next = data.get("data", {}).get("next")
            api_previous = data.get("data", {}).get("previous")

            
            col_info1, col_info2 = st.columns([3, 1])
            col_info1.success(f"Página {st.session_state.page} - Mostrando {len(results)} de {count} resultados")
            
            
            if results:
                df = pd.DataFrame(results)
                
                
                mapa_colunas = {
                    'name': 'Nome', 'height': 'Altura', 'mass': 'Massa', 
                    'gender': 'Gênero', 'birth_year': 'Ano Nasc.',
                    'climate': 'Clima', 'terrain': 'Terreno', 'population': 'População',
                    'model': 'Modelo', 'manufacturer': 'Fabricante', 'cost_in_credits': 'Custo',
                    'title': 'Título', 'director': 'Diretor', 'release_date': 'Lançamento'
                }
                df = df.rename(columns=mapa_colunas)
                
                
                cols_to_show = []
                if cat_to_use == 'people':
                    cols_to_show = ['Nome', 'Altura', 'Massa', 'Gênero', 'Ano Nasc.']
                elif cat_to_use == 'planets':
                    cols_to_show = ['Nome', 'Clima', 'Terreno', 'População']
                elif cat_to_use == 'starships':
                    cols_to_show = ['Nome', 'Modelo', 'Fabricante', 'Custo']
                elif cat_to_use == 'films':
                    cols_to_show = ['Título', 'Diretor', 'Lançamento']
                
                cols_final = [c for c in cols_to_show if c in df.columns]
                st.dataframe(df[cols_final] if cols_final else df, use_container_width=True)
            else:
                st.warning("Nenhum resultado nesta página.")

            
            col_prev, col_spacer, col_next = st.columns([1, 4, 1])
            
            with col_prev:
                if api_previous:
                    if st.button("⬅️ Anterior"):
                        st.session_state.page -= 1
                        st.rerun() 
            
            with col_next:
                if api_next:
                    if st.button("Próxima ➡️"):
                        st.session_state.page += 1
                        st.rerun() 

            with st.expander("Ver JSON Bruto"):
                st.json(data)

        elif response:
            st.error(f"Erro na API: {response.status_code}")
        else:
            st.error("🚨 Backend offline. Verifique o terminal.")