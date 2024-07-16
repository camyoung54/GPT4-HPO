from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

def query_hpo_api(term):
    base_url = "https://ontology.jax.org/api/hp"
    response = requests.get(f"{base_url}/terms?filter={term}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for term: {term}, status code: {response.status_code}")
        return None

def get_term_details(term_id):
    base_url = "https://ontology.jax.org/api/hp"
    response = requests.get(f"{base_url}/terms/{term_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for term ID: {term_id}, status code: {response.status_code}")
        return None

def extract_terms(case_report):
    # Simple regex to find potential medical terms (this can be improved)
    terms = re.findall(r'\b[a-zA-Z]+\b', case_report)
    # Convert to lower case and remove duplicates
    return list(set(map(str.lower, terms)))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_report = request.form['case_report']
        terms = extract_terms(case_report)
        term_details = []

        for term in terms:
            term_data = query_hpo_api(term)
            if term_data:
                for data in term_data:
                    details = get_term_details(data["id"])
                    if details:
                        term_details.append(details)
                    else:
                        term_details.append({"id": data["id"], "error": "Details not found"})
            else:
                term_details.append({"term": term, "error": "No data found"})

        return jsonify(term_details)

    return render_template_string('''
        <form method="post">
            Case Report: <textarea name="case_report" rows="10" cols="30"></textarea><br>
            <input type="submit">
        </form>
    ''')

if __name__ == "__main__":
    app.run(port=8000)
