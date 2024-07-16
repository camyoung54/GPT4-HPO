from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def query_hpo_api(term):
    base_url = "https://ontology.jax.org/api/hp"
    response = requests.get(f"{base_url}/terms?filter={term}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for term: {term}")
        return None

def get_term_details(term_id):
    base_url = "https://ontology.jax.org/api/hp"
    response = requests.get(f"{base_url}/terms/{term_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for term ID: {term_id}")
        return None

@app.route('/query', methods=['GET'])
def query_hpo():
    symptoms = request.args.getlist('symptoms')
    term_details = []

    for symptom in symptoms:
        terms = query_hpo_api(symptom)
        if terms:
            for term in terms:
                details = get_term_details(term["id"])
                if details:
                    term_details.append(details)

    return jsonify(term_details)

if __name__ == "__main__":
    app.run(port=8000)
