import os
from dotenv import load_dotenv
from shiny import App, ui, reactive, render
from openai import AsyncOpenAI
import asyncio
import requests

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
aclient = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to query the Clinical Tables HPO API
async def query_hpo_api(term):
    api_url = f"https://clinicaltables.nlm.nih.gov/api/hpo/v3/search?terms={term}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Patient Case Report Analysis Tool"),
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
    ui.h3("GPT4HPO Response", id="response_header", style="display:none; margin-top: 20px;"),  # Add margin-top for spacing
    ui.output_text_verbatim("output_area"),  # Use output_text_verbatim for displaying the response
    ui.output_text_verbatim("output"),
    ui.output_text_verbatim("error")
)

# Define the server logic
def server(input, output, session):

    result_reactive = reactive.Value("")
    error_reactive = reactive.Value("")
    response_header_visible = reactive.Value(False)

    @reactive.Effect
    @reactive.event(input.submit)
    async def process_case_report():
        case_report = input.case_report()
        try:
            log = []
            log.append("Submitting request to HPO API...")
            print("Submitting request to HPO API...")

            # Extract terms from the case report (basic example: you might need a more sophisticated method)
            terms = case_report.split()
            hpo_terms_info = []

            for term in terms:
                hpo_response = await query_hpo_api(term)
                if hpo_response and len(hpo_response) > 2 and isinstance(hpo_response[3], list):
                    hpo_terms_info.extend(hpo_response[3])

            # Flatten the list and join terms into a string
            hpo_terms_info_str = "\n".join([item for sublist in hpo_terms_info for item in (sublist if isinstance(sublist, list) else [sublist])])
            log.append("Received response from HPO API.")
            print("Received response from HPO API:", hpo_terms_info_str)

            log.append("Submitting request to GPT-4...")
            print("Submitting request to GPT-4...")

            # Query GPT-4 with additional information
            refined_prompt = f"Given the following patient case report and related medical terms, list the potential differential diagnoses and broad disease categories:\n\nCase Report:\n{case_report}\n\nRelated Medical Terms:\n{hpo_terms_info_str}"
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
