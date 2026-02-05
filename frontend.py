import streamlit as st
import requests
import pandas as pd


st.set_page_config(page_title="Explorador Star Wars", page_icon="⚔️", layout="wide")
st.title("🌌 Explorador Star Wars")


if 'page' not in st.session_state: st.session_state.page = 1


tradutor_conteudo = {
    
    "male": "Masculino", "female": "Feminino", "n/a": "N/A", "none": "Nenhum", "hermaphrodite": "Hermafrodita",
    
    "blue": "Azul", "brown": "Castanho", "green": "Verde", "red": "Vermelho", 
    "black": "Preto", "blond": "Loiro", "white": "Branco", "grey": "Cinza", "yellow": "Amarelo",
    
    "arid": "Árido", "temperate": "Temperado", "tropical": "Tropical", "frozen": "Congelado", "murky": "Obscuro"
}


tradutor_colunas = {
    'name': 'Nome', 'height': 'Altura (cm)', 'mass': 'Massa (kg)', 
    'gender': 'Gênero', 'birth_year': 'Ano Nasc.', 'hair_color': 'Cor Cabelo', 'eye_color': 'Cor Olhos',
    'climate': 'Clima', 'terrain': 'Terreno', 'population': 'População',
    'model': 'Modelo', 'manufacturer': 'Fabricante', 'cost_in_credits': 'Custo', 'passengers': 'Passageiros',
    'title': 'Título', 'director': 'Diretor', 'release_date': 'Lançamento', 'episode_id': 'Episódio'
}


st.sidebar.header("Filtros de Busca")


mapa_categorias = {"Personagens": "people", "Planetas": "planets", "Naves": "starships", "Filmes": "films"}
cat_visual = st.sidebar.selectbox("Escolha a Categoria:", list(mapa_categorias.keys()))
cat_api = mapa_categorias[cat_visual]

if 'ultima_categoria' not in st.session_state:
    st.session_state.ultima_categoria = cat_api

if st.session_state.ultima_categoria != cat_api:
    st.session_state.page = 1
    st.session_state.ultima_categoria = cat_api
    st.rerun()

sort_option = st.sidebar.selectbox("Ordenar por:", ["Padrão (ID)", "Nome / Título"])

sort_api = "name" if sort_option == "Nome / Título" and cat_api != "films" else "title" if sort_option == "Nome / Título" else None


search = st.sidebar.text_input("Pesquisar (Nome):")


if st.sidebar.button("Buscar Dados 🔎"): 
    st.session_state.page = 1
    st.rerun()


api_url = "http://localhost:8080/"
params = {
    "category": cat_api, 
    "search": search, 
    "page": st.session_state.page,
    "sort": sort_api
}

try:
    
    with st.spinner("Consultando a Força..."):
        resp = requests.get(api_url, params=params)

    if resp.status_code == 200:
        data = resp.json()
        results = data.get("data", {}).get("results", [])
        total_count = data.get("data", {}).get("count", 0)
        
        
        col_nav1, col_nav2, col_nav3 = st.columns([1, 6, 1])
        with col_nav2:
            st.info(f"Página {st.session_state.page} - Exibindo {len(results)} de {total_count} registros")
        
        with col_nav1:
            if data['data'].get('previous'):
                if st.button("Anterior"):
                    st.session_state.page -= 1
                    st.rerun()
        with col_nav3:
            if data['data'].get('next'):
                if st.button("Próxima"):
                    st.session_state.page += 1
                    st.rerun()

        
        if results:
            df = pd.DataFrame(results)
            
            
            df = df.replace(tradutor_conteudo)

            
            df = df.rename(columns=tradutor_colunas)
            
            
            cols_to_show = []
            if cat_api == 'people':
                cols_to_show = ['Nome', 'Altura (cm)', 'Massa (kg)', 'Gênero', 'Cor Olhos']
            elif cat_api == 'planets':
                cols_to_show = ['Nome', 'Clima', 'Terreno', 'População']
            elif cat_api == 'starships':
                cols_to_show = ['Nome', 'Modelo', 'Fabricante', 'Custo']
            elif cat_api == 'films':
                cols_to_show = ['Episódio', 'Título', 'Diretor', 'Lançamento']
            
            
            cols_final = [c for c in cols_to_show if c in df.columns]
            
            
            st.dataframe(df[cols_final] if cols_final else df, use_container_width=True)

            
            if cat_api == "films":
                st.divider() 
                st.subheader("🎬 Detalhes Estendidos (Processamento Paralelo)")
                
                
                filme_selecionado = st.selectbox(
                    "Selecione um filme para ver quem participou:",
                    df['Título'].unique(),
                    index=None,
                    placeholder="Escolha um filme..."
                )

                if filme_selecionado:
                    
                    filme_data = df[df['Título'] == filme_selecionado].iloc[0]
                    
                    filme_id = next((item['url'].split('/')[-2] for item in results if item['title'] == filme_selecionado), None)

                    if filme_id and st.button(f"Carregar Personagens de '{filme_selecionado}'"):
                        with st.spinner("Buscando nomes simultaneamente (Threads)..."):
                            
                            detail_params = {
                                "category": "films", 
                                "id": filme_id, 
                                "expand": "characters"
                            }
                            resp_detalhe = requests.get(api_url, params=detail_params)
                            
                            if resp_detalhe.status_code == 200:
                                nomes_chars = resp_detalhe.json()['data'].get('character_names', [])
                                st.success(f"Personagens encontrados: {len(nomes_chars)}")
                                
                                st.write(", ".join([f"**{n}**" for n in nomes_chars]))
                            else:
                                st.error("Erro ao carregar detalhes.")

        else:
            st.warning("Nenhum resultado encontrado.")

    else:
        st.error(f"Erro de conexão com o Backend: {resp.status_code}")

except Exception as e:
    st.error(f"Backend offline ou erro de conexão. Verifique o terminal.\nDetalhe: {e}")