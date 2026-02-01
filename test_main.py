import pytest
from unittest.mock import patch, Mock
import main
import flask

@pytest.fixture
def app():
    # Cria uma aplicação Flask simulada para contexto de teste
    app = flask.Flask(__name__)
    with app.test_request_context():
        yield app

def test_invalid_category(app):
    # Simula uma requisição com categoria errada
    req = Mock(args={'category': 'invalid_stuff'})
    
    response, status_code = main.starwars_search(req)
    
    assert status_code == 400
    assert "Categoria inválida" in response.json['error']

@patch('main.requests.get')
def test_search_luke(mock_get, app):
    # Simula o sucesso da busca pelo Luke sem chamar a API de verdade
    req = Mock(args={'category': 'people', 'search': 'Luke'})
    
    # Mock da resposta da SWAPI
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"name": "Luke Skywalker"}]}
    mock_get.return_value = mock_response

    response, status_code = main.starwars_search(req)

    assert status_code == 200
    assert response.json['data']['results'][0]['name'] == "Luke Skywalker"
    # Verifica se a URL chamada estava correta
    mock_get.assert_called_with("https://swapi.dev/api/people/?search=Luke")