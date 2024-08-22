from flask import Flask, request, send_file, render_template
import pandas as pd
from io import BytesIO, StringIO


from llama_index.llms.perplexity import Perplexity
from pydantic import BaseModel

class Question(BaseModel):
    response: str

class StockQuestion(BaseModel):
    earningsQuestion: Question
    currentNewsQuestion: Question
    themeQuestion: Question
    ratingQuestion: Question

from llama_index.core.program import LLMTextCompletionProgram

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_stocks():
    csv_file = request.files['csvFile']
    api_key = request.form['apiKey']
    
    # Read CSV file into a DataFrame
    csv_data = csv_file.read().decode('utf-8')
    data = StringIO(csv_data)
    df = pd.read_csv(data, skiprows=3)
    
    # Convert the 'Symbol' column to a list of ticker symbols
    tickers = df['Symbol'].tolist()
    
    # Initialize Perplexity LLM
    llm = Perplexity(
        api_key=api_key, model="llama-3.1-sonar-small-128k-online", temperature=0
    )
    
    prompt_template_str = """Answer the following questions pertaining to the ticker symbol {ticker_symbol}.
    1. Earnings Questions: What is the recent earnings trend for {ticker_symbol}?
    2. Current News Questions: What is the latest news on {ticker_symbol}?
    3. Theme Questions: Are there any major themes (ie. COVID in 2020) related to {ticker_symbol}?
    4. Rating Questions: How would you rate this {ticker_symbol} on a scale of A to E and why?
    """
    
    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_cls=StockQuestion,
        prompt_template_str=prompt_template_str
    )
    
    responses: dict[str, StockQuestion] = {}
    for ticker in tickers:
        responses[ticker] = program(ticker_symbol=ticker)
        
    parsed_responses = {
        ticker: {
            "Earnings Question": output.earningsQuestion.response,
            "Current News Question": output.currentNewsQuestion.response,
            "Theme Question": output.themeQuestion.response,
            "Rating": output.ratingQuestion.response
        } for ticker, output in responses.items()
    }
    
    # Generate the CSV file
    response_df = pd.DataFrame(parsed_responses).T
    csv_output = response_df.to_csv(index=False)
    
    # Send the CSV file as a response
    csv_bytes = csv_output.encode('utf-8')
    return send_file(BytesIO(csv_bytes), download_name='responses.csv', as_attachment=True)

if __name__ == '__main__':
    app.run()