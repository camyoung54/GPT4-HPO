import os
from dotenv import load_dotenv
from shiny import App, ui, reactive, render
from openai import AsyncOpenAI
import asyncio

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
aclient = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Patient Case Report Analysis Tool"),
    ui.input_text_area("case_report", "Enter Patient Case Report:", placeholder="Type or paste the patient case report here...", rows=10),
    ui.input_action_button("submit", "Submit"),
    ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle-response-header', function(show) {
            if (show) {
                document.getElementById('response_header').style.display = 'block';
            } else {
                document.getElementById('response_header').style.display = 'none';
            }
        });
    """),
    ui.h3("Response", id="response_header", style="display:none;"),
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
    async def query_gpt4():
        case_report = input.case_report()
        try:
            print("Submitting request to GPT-4...")
            response = await asyncio.wait_for(
                aclient.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a medical expert."},
                        {"role": "user", "content": f"Given the following patient case report, list the potential differential diagnoses and broad disease categories:\n\n{case_report}"}
                    ],
                    max_tokens=500,  # Reduced max_tokens for faster response
                    temperature=0.7,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                ),
                timeout=30  # Timeout after 30 seconds
            )
            print("Received response from GPT-4.")
            
            # Debug: Print the response
            response_content = response.choices[0].message.content.strip()
            print("Response content:", response_content)
            
            result_reactive.set(response_content)
            error_reactive.set("")  # Clear any previous errors
            response_header_visible.set(True)  # Show the response header

        except asyncio.TimeoutError:
            print("Request to GPT-4 timed out.")
            error_reactive.set("Error: Request to GPT-4 timed out.")
            result_reactive.set("")  # Clear the result if there's an error
            response_header_visible.set(False)  # Hide the response header if there's an error

        except Exception as e:
            print(f"An error occurred: {e}")
            error_reactive.set(f"Error: {str(e)}")
            result_reactive.set("")  # Clear the result if there's an error
            response_header_visible.set(False)  # Hide the response header if there's an error

    @render.text
    def output_text():
        # Debug: Print the current result
        current_result = result_reactive.get()
        print("output_text called. Current result:", current_result)
        return current_result

    @render.text
    def error_text():
        return error_reactive.get()

    output.output = output_text
    output.error = error_text

    # Control the visibility of the response header
    @reactive.Effect
    async def update_response_header():
        await session.send_custom_message('toggle-response-header', response_header_visible.get())

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
