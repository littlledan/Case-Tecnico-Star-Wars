import functions_framework
import requests
import flask
from concurrent.futures import ThreadPoolExecutor

def fetch_name(url):
    """Função auxiliar para buscar o nome de uma URL específica."""
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json().get('name')
    except:
        return None
    return None

@functions_framework.http
def starwars_search(request):
    """
    Cloud Function com suporte a:
    - Paginação
    - Ordenação (Sort)
    - Expansão de dados correlacionados (Parallel Fetching)
    """
    request_args = request.args
    category = request_args.get('category', 'people')
    search_term = request_args.get('search')
    resource_id = request_args.get('id')
    page = request_args.get('page', '1')
    sort_field = request_args.get('sort') 
    expand = request_args.get('expand')   
    
    base_url = "https://swapi.dev/api"
    
    
    allowed_categories = ['people', 'planets', 'starships', 'films']
    if category not in allowed_categories:
        return flask.jsonify({"error": "Categoria inválida"}), 400

    
    if resource_id:
        target_url = f"{base_url}/{category}/{resource_id}/"
    else:
        target_url = f"{base_url}/{category}/"
        params = []
        if search_term: params.append(f"search={search_term}")
        if page: params.append(f"page={page}")
        if params: target_url += "?" + "&".join(params)

    try:
        response = requests.get(target_url)
        if response.status_code == 404:
            return flask.jsonify({"message": "Não encontrado"}), 404
        response.raise_for_status()
        
        data = response.json()
        
        
        if sort_field and 'results' in data:
            
            data['results'] = sorted(
                data['results'], 
                key=lambda x: x.get(sort_field, "").lower() if isinstance(x.get(sort_field), str) else x.get(sort_field, 0)
            )

        
        if category == 'films' and resource_id and expand == 'characters':
            character_urls = data.get('characters', [])
            
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                names = list(executor.map(fetch_name, character_urls))
            
            
            data['character_names'] = [n for n in names if n]

        return flask.jsonify({
            "source": "GCP Cloud Function",
            "query_params": {
                "category": category,
                "sort": sort_field,
                "expand": expand
            },
            "data": data
        }), 200

    except requests.exceptions.RequestException as e:
        return flask.jsonify({"error": "Erro SWAPI", "details": str(e)}), 500