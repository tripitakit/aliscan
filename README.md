# aliscan (v1.1)

## Overview

Aliscan is a tool for analyzing nucleotide sequence alignments to identify signature patterns. It provides a web interface for uploading, configuring, and visualizing sequence alignments with color-coded scoring based on nucleotide position significance.

## Features

- **Web Interface**: Upload and analyze alignment files through a user-friendly web interface
- **Group-Based Analysis**: Create custom sequence groups for comparative analysis
- **Configurable Parameters**: Adjust scoring parameters for consensus (ka) and aspecificity (kb)
- **Visual Results**: Color-masked alignment visualization with score highlighting
- **Downloadable Results**: Export analysis results in HTML format
- **Persistent Storage**: SQLite database for reliable session state management
- **Multi-user Support**: Separate sessions for concurrent users

## Requirements

- **Python 3.6 or higher**: Core programming language used for the application
- **Flask 2.2.3**: Web framework for building the application's interface
- **Werkzeug 2.2.3**: WSGI utility library for handling HTTP requests and serving the web application
- **BioPython 1.81**: Library for biological computation, used for processing and analyzing nucleotide sequences
- **SQLite3**: Included in Python's standard library, used for state persistence

## Installation

### Clone the repository

```bash
git clone https://github.com/tripitakit/aliscan.git
cd aliscan
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface

1. Start the web server:

```bash
python app.py
```

2. Open a browser and navigate to `http://127.0.0.1:5000/`

3. Follow the steps in the web interface:
   - Upload a FASTA alignment file
   - Define sequence groups for analysis
   - Configure analysis parameters
   - Run the scan and view results

### Parameters

Aliscan uses two main parameters to control the analysis:

- **ka (Consensus coefficient)**:

  - 20: Strict consensus requirement
  - 10: High consensus (majority rule high)
  - 3: Low consensus (majority rule low)
  - **Custom values**: Any value between 0-100 can be set using the numeric input

- **kb (Aspecificity tolerance)**:
  - 20: Forbid appearance in outgroup
  - 10: Penalize appearance in outgroup
  - **Custom values**: Any value between 0-100 can be set using the numeric input

### Scoring Formula

The scoring formula used is: `1 - (ka*0.5)*(1-a) - (kb*0.1)*b`

Where:

- **a**: frequency of the nucleotide in the ingroup (consensus)
- **b**: frequency of the nucleotide in the outgroup (aspecificity)
- **ka**: consensus coefficient
- **kb**: aspecificity tolerance coefficient

## Formula Editing Functionality

AliScan includes a customizable scoring formula feature that allows you to fine-tune how sequence alignments are evaluated:

### Available Variables and Coefficients

- **a**: Frequency of a residue in the ingroup (0-1)
- **b**: Frequency of a residue in the outgroup (0-1)
- **ka**: Consensus coefficient (preset values of 20, 10, or 3, or any custom value between 0-100)
- **kb**: Aspecificity tolerance (preset values of 20 or 10, or any custom value between 0-100)

### Supported Math Functions

- Basic operations: `+`, `-`, `*`, `/`, `()` for grouping
- Trigonometric: `sin`, `cos`, `tan`
- Other functions: `abs`, `max`, `min`, `pow`, `round`

### Default Formula

```
1 - (ka*0.5)*(1-a) - (kb*0.1)*b
```

This formula evaluates each position by penalizing positions with low ingroup consensus (first term) and high outgroup frequency (second term).

You can modify this formula in the results page to customize the alignment analysis to your specific research needs.

## Example Usage (Python API)

```python
import aliscan

# Initialize state
state = aliscan.create_state()

# Load alignment file
state = aliscan.load_alignment(state, "alignment.fasta")

# Set sequence groups
state = aliscan.set_groups(state, [[0, 1, 2], [3, 4, 5]])

# Set analysis parameters
state = aliscan.set_ka(state, 10)
state = aliscan.set_kb(state, 10)

# Run the scan
state = aliscan.scan(state)

# Generate HTML output
aliscan.scores2html(state, "results.html")
```

## Architecture

Aliscan consists of three main components:

1. **aliscan.py**: Core library that handles sequence alignment processing and scoring
2. **app.py**: Flask web application that provides the user interface and handles HTTP requests
3. **db.py**: Database module that manages state persistence using SQLite

The application uses a functional approach where the state is never modified in-place but instead each function returns a new state object. This state is stored in an SQLite database between requests for persistence.

## Data Storage

- **Session data**: Stored in an SQLite database (`aliscan.db`)
- **Uploaded files**: Stored in the `uploads` directory
- **Results**: Generated as HTML files in the `uploads` directory with unique session IDs

## Color Coding

The output alignment is color-coded based on the calculated scores:

- **White**: Score < 0.5
- **Blue**: Score between 0.5 and 0.7
- **Green**: Score between 0.7 and 0.8
- **Yellow**: Score between 0.8 and 0.9
- **Red**: Score > 0.9

## File Format Support

Aliscan accepts FASTA format multiple sequence alignment files (.fasta, .fa, .aln).

## Contributing

Contributions to improve aliscan are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [COPYING](COPYING) file for details.

## Contact

Author: Patrick De Marta  
Email: patrick.demarta@gmail.com
