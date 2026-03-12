# N.A.P - A News API Pipeline

```txt
░▒▓███████▓▒░        ░▒▓██████▓▒░       ░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░      ░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓██▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓██▓▒░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓██▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓██▓▒░▒▓█▓▒░        
```

N.A.P. (News API Pipeline) is a robust ETL (Extract, Transform, Load) solution that fetches automated news data from NewsData.io, processes it, and stores it in a structured database. The project serves as a bridge between raw API data and analytical reports.

## Project Structure

```bash
├── data                # Local storage for raw and processed data
├── docs                # Project documentation and manuals
├── src                 # Modularized source code (logic & modules)
├── main.py             # Central orchestration script
├── report.qmd          # Quarto report for data analysis
├── _quarto.yaml        # Configuration for Quarto reporting
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── README.md           # Project documentation
```

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- A valid API key from NewsData.io

### 1. Clone Repository & Setup Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activation for Linux/macOS
source .venv/bin/activate

# Activation for Windows
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a .env file in the root directory (refer to .env.example):

```txt
API_KEY=YOUR_API_KEY_HERE
```

## Usage

To start the pipeline and execute the ETL process:

```bash
python main.py
```

To generate the analysis report using Quarto:

```bash
quarto render report.qmd
```

## License

This project is licensed under the MIT License.
