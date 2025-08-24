# Sentiment Analysis of Social Media Data

## 1. Project Overview

This project provides a comprehensive, end-to-end pipeline for performing sentiment analysis on social media data. It utilizes a Jupyter Notebook to walk through each stage of the process, from data collection and preprocessing to training multiple machine learning models, evaluating their performance, and visualizing the results. The primary goal is to classify tweets into positive, negative, or neutral sentiments.

This notebook is designed to be a clear and reusable template for sentiment analysis tasks, with detailed explanations and easily modifiable parameters.

## 2. Features

- **Data Collection:** Includes a placeholder for live data collection from Twitter (using Tweepy) and a fallback to a sample CSV for immediate use.
- **Data Cleaning:** A robust text preprocessing pipeline to clean and standardize raw tweet data.
- **Dual Text Representation:** Implements and compares both classical TF-IDF and modern BERT-based text representations.
- **Multi-Model Training:** Trains and evaluates three distinct models: Multinomial Naive Bayes, Support Vector Machine (SVM), and a fine-tuned BERT transformer.
- **In-Depth Evaluation:** Uses a wide range of metrics (Accuracy, Precision, Recall, F1-Score) and visualizes performance with confusion matrices.
- **Hyperparameter Tuning:** Demonstrates how to optimize a model's performance using `GridSearchCV`.
- **Rich Visualizations:** Generates insightful plots, including sentiment distributions, word clouds for positive/negative terms, and a final summary dashboard.
- **Organized Output:** Automatically saves all outputs, including the cleaned dataset, evaluation scores, trained models, and plots, into designated folders.

## 3. Project Structure

The project is organized into the following directories and files:

```
. 
├── data/ # (Optional) For storing raw and processed datasets.
├── models/ # Stores the trained and saved model files (.pkl, .pth).
├── plots/ # Stores all generated visualizations (.png).
├── results/ # Stores the model evaluation scores (.json).
├── analysis.ipynb # The main Jupyter Notebook.
├── sample_tweets.csv # A sample input dataset to ensure the notebook is runnable.
├── requirements.txt # A list of all Python dependencies.
└── README.md # This file.
```

## 4. Setup and Installation

Follow these steps to set up your local environment and run the project.

**Prerequisites:**
- Python 3.8 or higher

**Step 1: Clone the Repository & Create a Virtual Environment**

```bash
# Navigate to your desired directory and clone the repository (if applicable)
# git clone <repository-url>
# cd <repository-name>

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# .\venv\Scripts\activate
```

**Step 2: Configure Environment Variables**

This project uses a `.env` file to securely manage the Twitter API key. 

1.  Create a file named `.env` in the root project directory.
2.  Open the file and add your API key in the following format:

```
BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"
```

This file is included in `.gitignore`, so your secret key will not be committed to version control.

**Step 3: Install Dependencies**

Install all the required libraries using the `requirements.txt` file. This now includes `python-dotenv` to load the environment file.

```bash
pip install -r requirements.txt
```

**Step 4: Launch Jupyter Notebook**

```bash
jupyter notebook
```

This will open a new tab in your web browser. Navigate to and open the `analysis.ipynb` file.

## 5. How to Run the Notebook

The notebook is designed to be run sequentially from top to bottom. 

1.  Open `analysis.ipynb` in Jupyter.
2.  Click on the first code cell.
3.  Execute each cell by pressing `Shift + Enter` or by clicking the "Run" button in the toolbar.
4.  The first time you run the setup cell, it will download the necessary NLTK data (`stopwords` and `wordnet`).

## 6. Input and Output

- **Input Data:**
  - The project runs by default using the `sample_tweets.csv` file located in the root directory.
  - To use your own data, simply replace this file or modify the `csv_path` variable in the **Data Collection** section of the notebook.

- **Output Files (Logs & Results):**
  - **Cleaned Data:** The processed and cleaned dataset is saved to `cleaned_data.csv`.
  - **Evaluation Metrics:** A detailed comparison of the models' performance is saved in `results/evaluation_results.json`.
  - **Plots and Charts:** All visualizations, including the final dashboard, are saved as `.png` files in the `plots/` directory.
  - **Trained Models:** The trained Naive Bayes, SVM, and BERT models are saved in the `models/` directory.

## 7. How to Modify the Notebook

The notebook is designed for easy customization. Look for Markdown cells or code comments labeled **`--- How to Modify ---`** for key parameters you can change.

**Key areas for modification include:**

1.  **Using Live Twitter Data:**
    - First, ensure you have added your `BEARER_TOKEN` to the `.env` file as described in the setup instructions.
    - In the **Data Collection** section (Cell #4), change the variable `USE_LIVE_DATA` to `True`.

2.  **Train-Test Split Ratio:**
    - In the **Splitting Data** section (Cell #9), you can change the `test_size` parameter (e.g., from `0.2` to `0.3` to use 30% of the data for testing).

3.  **TF-IDF Parameters:**
    - In the **TF-IDF Vectorization** section (Cell #11), you can adjust:
      - `ngram_range`: Change `(1, 2)` to `(1, 1)` to only use single words instead of two-word phrases.
      - `max_features`: Decrease or increase the vocabulary size from `5000`.

4.  **Model Hyperparameters:**
    - **Naive Bayes:** Adjust the `alpha` smoothing parameter in Cell #13.
    - **SVM:** Change the `C` and `kernel` parameters in Cell #15.
    - **BERT:** Modify the `learning_rate`, `batch_size`, or `epochs` in Cell #17.

5.  **Hyperparameter Tuning (GridSearchCV):**
    - In the **Hyperparameter Tuning** section (Cell #24), you can expand the `param_grid` dictionary to search over more SVM parameters and values.
