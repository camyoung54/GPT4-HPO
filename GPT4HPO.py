import os
from dotenv import load_dotenv, dotenv_values
from shiny import App, ui, reactive, render
from openai import AsyncOpenAI
import asyncio
import requests

# Clear any existing environment variables that might conflict
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

#test
# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
aclient = AsyncOpenAI(api_key=api_key)

# Function to query the Clinical Tables HPO API
async def query_hpo_api(term):
    api_url = f"https://clinicaltables.nlm.nih.gov/api/hpo/v3/search?terms={term}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to extract unique terms from the case report
def extract_terms(case_report):
    terms = set(case_report.split())  # Using set to get unique terms
    return list(terms)

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("GPT-4 HPO Differential Diagnosis Tool"),
    ui.h5("The GPT-4 HPO Differential Diagnosis Tool is a web application designed to analyze pediatric patient case reports and provide potential differential diagnoses and broad disease categories using GPT-4 from OpenAI. The tool enhances its accuracy by first querying the Human Phenotype Ontology (HPO) API for related medical terms, which are then included in the prompt to GPT-4."),
    ui.input_text_area("case_report", "Enter Patient Case Report:", placeholder="Type or paste the patient case report here...", rows=10, width="100%"),
    ui.input_action_button("submit", "Submit"),
    ui.br(),  # Add a line break for additional space
    ui.br(),  # Add another line break for more space
    ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle-response-header', function(show) {
            if (show) {
                document.getElementById('response_header').style.display = 'block';
            } else {
                document.getElementById('response_header').style.display = 'none';
            }
        });
    """),
    ui.h3("GPT-4 HPO Response:", id="response_header", style="display:none; margin-top: 20px;"),  # Add margin-top for spacing
    ui.output_text_verbatim("output_area"),  # Use output_text_verbatim for displaying the response
    ui.output_text_verbatim("output"),
    ui.output_text_verbatim("error")
)

# Define the server logic
def server(input, output, session):

    result_reactive = reactive.Value("")
    error_reactive = reactive.Value("")
    response_header_visible = reactive.Value(False)

    async def call_gpt4_with_retry(refined_prompt, max_retries=3, initial_delay=2):
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    aclient.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a medical expert."},
                            {"role": "user", "content": refined_prompt}
                        ],
                        max_tokens=500,  # Reduced max_tokens for faster response
                        temperature=0.7,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0
                    ),
                    timeout=30  # Timeout after 30 seconds
                )
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error occurred: {e}. Retrying in {initial_delay} seconds...")
                    await asyncio.sleep(initial_delay)
                    initial_delay *= 2
                else:
                    raise e

    @reactive.Effect
    @reactive.event(input.submit)
    async def process_case_report():
        case_report = input.case_report()
        try:
            log = []
            log.append("Submitting request to HPO API...")
            print("Submitting request to HPO API...")

            terms = extract_terms(case_report)
            hpo_terms_info = []

            for term in terms:
                hpo_response = await query_hpo_api(term)
                if hpo_response and len(hpo_response) > 2 and isinstance(hpo_response[3], list):
                    for item in hpo_response[3]:
                        if isinstance(item, str):
                            hpo_terms_info.append(item)
                        elif isinstance(item, list):
                            hpo_terms_info.extend(item)

            # Limiting the number of terms to prevent exceeding the token limit
            hpo_terms_info = hpo_terms_info[:50]

            # Ensure all items in hpo_terms_info are strings and join them into a single string
            hpo_terms_info_str = "\n".join(hpo_terms_info)
            log.append("Received response from HPO API.")
            print("Received response from HPO API:", hpo_terms_info_str)

            # Limit the case report length to avoid exceeding the context length
            case_report = case_report[:2000]

            log.append("Submitting request to GPT-4...")
            print("Submitting request to GPT-4...")

            # Query GPT-4 with additional information
            refined_prompt = f"Given the following patient case report and related medical terms, list the potential differential diagnoses and broad disease categories:\n\nCase Report:\n{case_report}\n\nRelated Medical Terms:\n{hpo_terms_info_str}"
            response = await call_gpt4_with_retry(refined_prompt)

            log.append("Received response from GPT-4.")
            print("Received response from GPT-4.")

            # Debug: Print the response
            response_content = response.choices[0].message.content.strip()
            log.append(f"Response content: {response_content}")
            print("Response content:", response_content)

            result_reactive.set(response_content)
            error_reactive.set("")  # Clear any previous errors
            response_header_visible.set(True)  # Show the response header

        except asyncio.TimeoutError:
            log.append("Request to GPT-4 timed out.")
            print("Request to GPT-4 timed out.")
            error_reactive.set("Error: Request to GPT-4 timed out.")
            result_reactive.set("\n".join(log))
            response_header_visible.set(False)  # Hide the response header if there's an error

        except Exception as e:
            log.append(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            error_reactive.set(f"Error: {str(e)}")
            result_reactive.set("\n".join(log))
            response_header_visible.set(False)  # Hide the response header if there's an error

    @render.text
    def output_text():
        # Debug: Print the current result
        current_result = result_reactive.get()
        print("output_text called. Current result:", current_result)
        return current_result

    @render.text
    def error_text():
        current_error = error_reactive.get()
        print("error_text called. Current error:", current_error)
        return current_error

    @render.text
    def output_area():
        return result_reactive.get()

    output.output = output_text
    output.error = error_text
    output.output_area = output_area

    # Control the visibility of the response header
    @reactive.Effect
    async def update_response_header():
        await session.send_custom_message('toggle-response-header', response_header_visible.get())

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
