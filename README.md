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
.
├── data                # Local storage for raw and processed data
├── docs                # Project documentation and manuals
├── LICENSE             # Project license
├── main.py             # Central orchestration script
├── plots               # Plot code and outputs
├── _quarto.yaml        # Configuration for Quarto reporting
├── README.md           # Project documentation
├── report              # Quarto report dir for data analysis
├── requirements.txt    # Python dependencies
└── src                 # Modularized source code (logic & modules)        
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

Create a .env file in the root directory:

```txt
API_KEY=YOUR_API_KEY_HERE
```

## Usage

To start the pipeline and execute the ETL process:

```bash
python3 main.py
python3 src/processor.py
python3 src/merge.py
```

To generate the analysis report using Quarto:

```bash
quarto render report/output.qmd
```
## Code Contributions

### Nils Rechberger

Nils served as the technical lead for the project. He was responsible for managing the GitHub repository, overseeing pull requests, and ensuring code quality. Additionally, he developed both the Proof of Concept (POC) and the Minimum Viable Product (MVP).

### Petronela Tabalae

Petronela held a hybrid role, bridging the gap between technical implementation and academic documentation. She was primarily responsible for coding the plots, authoring the final report and refining the team’s written deliverables.

### Khrystyna Masliak

Khrystyna was responsible for refining and scaling the final codebase. She extended the MVP’s scope, implemented large-scale data export functionality, and managed the data merging process.

> Note: Petronela and Khrystyna worked collaboratively on-site; as a result, some of Khrystyna’s contributions are reflected in shared commits rather than individual ones.

## License

This project is licensed under the MIT License.

