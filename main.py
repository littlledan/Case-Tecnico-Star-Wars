import functions_framework
import requests
import flask

@functions_framework.http
def starwars_search(request):
    """
    Cloud Function para buscar dados na SWAPI com suporte a PAGINAÇÃO.
    """
    request_args = request.args
    category = request_args.get('category', 'people')
    search_term = request_args.get('search')
    resource_id = request_args.get('id')
    page = request_args.get('page', '1')
    
    base_url = "https://swapi.dev/api"
    
    allowed_categories = ['people', 'planets', 'starships', 'films']
    if category not in allowed_categories:
        return flask.jsonify({
            "error": "Categoria inválida", 
            "valid_options": allowed_categories
        }), 400

    
    if resource_id:
        target_url = f"{base_url}/{category}/{resource_id}/"
    else:
        target_url = f"{base_url}/{category}/"
        
        
        params = []
        if search_term:
            params.append(f"search={search_term}")
        if page:
            params.append(f"page={page}")
        
        
        if params:
            target_url += "?" + "&".join(params)

    try:
        response = requests.get(target_url)
        
        if response.status_code == 404:
            return flask.jsonify({"message": "Recurso não encontrado"}), 404
            
        response.raise_for_status()
        data = response.json()
        
        return flask.jsonify({
            "source": "GCP Cloud Function (Simulated)",
            "query_params": {
                "category": category,
                "search": search_term,
                "page": page
            },
            "data": data
        }), 200

    except requests.exceptions.RequestException as e:
        return flask.jsonify({"error": "Falha na comunicação com SWAPI", "details": str(e)}), 500