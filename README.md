# GPT-4 HPO Differential Diagnosis Tool

## Overview
The GPT-4 HPO Differential Diagnosis Tool is a web application designed to analyze patient case reports and provide potential differential diagnoses and broad disease categories using GPT-4 from OpenAI. The tool enhances its accuracy by first querying the Clinical Tables HPO API for related medical terms, which are then included in the prompt to GPT-4.

## Features
- User-friendly interface to input patient case reports.
- Queries Clinical Tables HPO API to extract related medical terms.
- Refines the GPT-4 prompt with additional context from HPO API results.
- Displays the response from GPT-4 with potential differential diagnoses and disease categories.

## Requirements
- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/gpt4-hpo-differential-diagnosis-tool.git
    cd gpt4-hpo-differential-diagnosis-tool
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your OpenAI API key:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. Run the application:
    ```bash
    python app.py
    ```

2. Open a web browser and navigate to `http://127.0.0.1:8000`.

3. Enter a patient case report in the input box and click "Submit".

4. View the response containing potential differential diagnoses and broad disease categories.

## Project Structure

```plaintext
├── app.py                  # Main application script
├── README.md               # Project documentation
├── requirements.txt        # List of dependencies
└── .env                    # Environment variables (not included in the repo)

## Example Case Report
```plaintext
A 45-year-old male presents with sudden onset ataxia, dizziness, and double vision. The patient has a history of hypertension and diabetes. Physical examination reveals nystagmus and dysmetria. MRI shows lesions in the cerebellum.
```
