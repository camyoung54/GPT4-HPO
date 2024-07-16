# HPO Query Automation

This project automates querying the HPO API and processing results for differential diagnosis.

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/camyoung54/GPT4-HPO.git
    cd GPT4-HPO
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    python app.py
    ```

5. Access the endpoint:
    ```sh
    http://localhost:8000/query?symptoms=bronchiolitis&symptoms=weight%20loss
    ```

## Usage

- To query the HPO API, send a GET request to `/query` with a list of symptoms as query parameters.

Example:
```sh
curl "http://localhost:8000/query?symptoms=bronchiolitis&symptoms=weight%20loss"
