import functions_framework
import requests
import flask

@functions_framework.http
def starwars_search(request):
    """
    Cloud Function para buscar dados na SWAPI.
    Projetada para rodar no GCP Cloud Functions.
    """
    # 1. Captura parâmetros (suporta GET via Query String)
    request_args = request.args
    category = request_args.get('category', 'people')
    search_term = request_args.get('search')
    resource_id = request_args.get('id')
    
    base_url = "https://swapi.dev/api"
    
    # Validação de segurança básica
    allowed_categories = ['people', 'planets', 'starships', 'films']
    if category not in allowed_categories:
        return flask.jsonify({
            "error": "Categoria inválida", 
            "valid_options": allowed_categories
        }), 400

    # 2. Montagem da URL
    if resource_id:
        target_url = f"{base_url}/{category}/{resource_id}/"
    else:
        target_url = f"{base_url}/{category}/"
        if search_term:
            target_url += f"?search={search_term}"

    # 3. Requisição à SWAPI
    try:
        response = requests.get(target_url)
        
        # Tratamento para 404 da SWAPI
        if response.status_code == 404:
            return flask.jsonify({"message": "Recurso não encontrado na SWAPI"}), 404
            
        response.raise_for_status()
        data = response.json()
        
        # 4. Resposta formatada
        return flask.jsonify({
            "source": "GCP Cloud Function (Simulated)",
            "query_params": {
                "category": category,
                "search": search_term
            },
            "data": data
        }), 200

    except requests.exceptions.RequestException as e:
        return flask.jsonify({"error": "Falha na comunicação com SWAPI", "details": str(e)}), 500