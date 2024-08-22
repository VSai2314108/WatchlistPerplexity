const { useState } = React;

const StockAnalysis = () => {
  const [csvFile, setCsvFile] = useState(null);
  const [apiKey, setApiKey] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
  
    const formData = new FormData();
    formData.append('csvFile', csvFile);
    formData.append('apiKey', apiKey);
  
    try {
      // notify user that the query is processing
      alert('Processing...');
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // get current date time as str
        const datetime = new Date().toISOString().slice(0, 19).replace('T', ' ');
        a.download = `Watchlist_Analysis_${datetime}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        alert('Downloaded to local machine path "Watchlist_Analysis.csv"');
      } else {
        console.error('Error:', response.status);
        // Handle error case, display an error message to the user
        const errorMessage = await response.text();
        alert(`An error occurred while processing the request: ${response.status} - ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error:', error);
      // Handle network or other errors, display an error message to the user
      const errorMessage = await response.text();
      alert(`An error occurred while processing the request: ${response.status} - ${errorMessage}`);
    }
  };

  return React.createElement(
    'div',
    null,
    React.createElement('h1', null, 'Stock Analysis'),
    React.createElement(
      'form',
      { onSubmit: handleSubmit },
      React.createElement(
        'div',
        null,
        React.createElement('label', { htmlFor: 'csvFile' }, 'Select CSV File:'),
        React.createElement('input', {
          type: 'file',
          id: 'csvFile',
          name: 'csvFile',
          accept: '.csv',
          onChange: (e) => setCsvFile(e.target.files[0]),
          required: true,
        })
      ),
      React.createElement(
        'div',
        null,
        React.createElement('label', { htmlFor: 'apiKey' }, 'Perplexity API Key:'),
        React.createElement('input', {
          type: 'text',
          id: 'apiKey',
          name: 'apiKey',
          value: apiKey,
          onChange: (e) => setApiKey(e.target.value),
          required: true,
        })
      ),
      React.createElement('button', { type: 'submit' }, 'Analyze Stocks')
    )
  );
};

ReactDOM.render(React.createElement(StockAnalysis, null), document.getElementById('root'));