from shiny import App, ui, reactive, render
import openai

# Initialize OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Patient Case Report Analysis Tool"),
    ui.input_text_area("case_report", "Enter Patient Case Report:", placeholder="Type or paste the patient case report here...", rows=10),
    ui.input_action_button("submit", "Submit"),
    ui.output_text_verbatim("diagnoses"),
    ui.output_text_verbatim("categories")
)

# Define the server logic
def server(input, output, session):
    
    @reactive.Effect
    @reactive.event(input.submit)
    def query_gpt4():
        case_report = input.case_report()
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the GPT-4 model
            prompt=f"Given the following patient case report, list the potential differential diagnoses and broad disease categories:\n\n{case_report}",
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7
        )
        result = response.choices[0].text.strip()
        
        # Separate differential diagnoses and disease categories
        diagnoses, categories = result.split("Broad disease categories:")
        diagnoses = diagnoses.replace("Differential diagnoses:", "").strip()
        categories = categories.strip()

        output.diagnoses.set(diagnoses)
        output.categories.set(categories)

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
