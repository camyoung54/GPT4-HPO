import os
from dotenv import load_dotenv
from shiny import App, ui, reactive, render
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
aclient = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Patient Case Report Analysis Tool"),
    ui.input_text_area("case_report", "Enter Patient Case Report:", placeholder="Type or paste the patient case report here...", rows=10),
    ui.input_action_button("submit", "Submit"),
    ui.output_text_verbatim("output")
)

# Define the server logic
def server(input, output, session):

    result_reactive = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.submit)
    async def query_gpt4():
        case_report = input.case_report()
        response = await aclient.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical expert."},
                {"role": "user", "content": f"Given the following patient case report, list the potential differential diagnoses and broad disease categories:\n\n{case_report}"}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        result = response.choices[0].message.content.strip()
        result_reactive.set(result)

    @render.text
    def output_text():
        return result_reactive.get()

    output.output = output_text

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
