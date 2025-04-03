# MAC-SQL Ukrainian Benchmark App

This Streamlit application provides a user-friendly interface for running and visualizing benchmarks of the MAC-SQL framework on the Ukrainian BIRD dataset.

## Features

- **Run Benchmarks**: Execute the MAC-SQL framework on random samples from the Ukrainian BIRD dataset
- **View Results**: Examine detailed results of your benchmark runs, including SQL queries and execution metrics
- **Compare Results**: Visualize performance across multiple benchmark runs with interactive charts

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/slowdown-macsql.git
   cd slowdown-macsql
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your PostgreSQL databases for the Ukrainian BIRD dataset (if not already done).

4. Create a `.env` file in the root directory with your API credentials:
   ```
   TOGETHER_API_KEY=your_api_key_here
   TOGETHER_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
   PG_USER=postgres
   PG_PASSWORD=your_password
   PG_HOST=localhost
   PG_PORT=5432
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the sidebar to configure your benchmark:
   - Set the data path to your BIRD-UKR dataset
   - Choose the number of samples
   - Select a random seed method

4. Run benchmarks with the buttons on the "Run Benchmark" tab:
   - "Run Quick Test" for a single sample
   - "Run Full Benchmark" for multiple samples
   - "Save Results" to store benchmark results

5. View past results in the "View Results" tab

6. Compare different benchmark runs in the "Compare Results" tab

## Buttons Explained

The app includes three main buttons for benchmarking:

1. **🚀 Run Quick Test**: Runs a quick test with a single sample. Useful for debugging or quick checks.

2. **🧪 Run Full Benchmark**: Runs a benchmark with the number of samples specified in the sidebar. Results are automatically saved.

3. **💾 Save Results**: Explicitly saves the current benchmark results to disk for later comparison.

## Tabs Explained

The app is organized into three tabs:

1. **Run Benchmark**: Execute benchmarks and view current results.

2. **View Results**: Browse and examine past benchmark results, including detailed SQL queries.

3. **Compare Results**: Compare metrics across multiple benchmark runs with visualizations.

## Output

Benchmark results are saved in the `output/bird_ukr/[timestamp]` directory, with the following information:

- Execution accuracy
- Number of samples
- Random seed used
- Average execution times
- Detailed results for each question

## Notes

- Make sure your PostgreSQL server is running before starting the app
- The app requires access to the BIRD-UKR dataset files
- Results are saved automatically when running a full benchmark 