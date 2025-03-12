# Aliscan (v1.1)

## Overview

Aliscan is a tool for visually analyzing nucleotide sequence alignments to identify signature patterns. It provides a web interface for uploading, configuring, and visualizing sequence alignments with color-coded scoring based on nucleotide position significance. It supports group-based analysis, allowing users to define custom sequence groups for comparative analysis.
Its scoring formula can be customized to fine-tune the analysis based on specific research requirements.
Aliscan can be used to identify conserved regions, detect mutations, and compare sequence patterns across multiple groups of sequences in a user-friendly and interactive manner. It is designed to be easy to use for biologists and researchers who need to to design taxon-specific PCR primers and qPCR/RT-qPCR probes, identify mutations, or study sequence conservation.

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
flask run
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

## Python API Reference

Aliscan provides a Python API for programmatic access to its functionality:

### State Management

#### `create_state()`

Creates a new empty state object.

**Returns:**

- A new state dictionary.

#### `load_alignment(state, filepath)`

Loads an alignment file into the state.

**Parameters:**

- `state`: The state dictionary.
- `filepath`: Path to the alignment file in FASTA format.

**Returns:**

- Updated state with alignment data.

#### `set_groups(state, groups)`

Sets the sequence groups for analysis.

**Parameters:**

- `state`: The state dictionary.
- `groups`: List of lists, where each inner list contains sequence indices for a group.

**Returns:**

- Updated state with group information.

### Parameter Configuration

#### `set_ka(state, ka)`

Sets the consensus coefficient parameter.

**Parameters:**

- `state`: The state dictionary.
- `ka`: Integer value for the consensus coefficient (typically 3, 10, or 20, but can be any integer between 0-100).

**Returns:**

- Updated state with new ka value.

#### `set_kb(state, kb)`

Sets the aspecificity tolerance parameter.

**Parameters:**

- `state`: The state dictionary.
- `kb`: Integer value for the aspecificity tolerance (typically 10 or 20, but can be any integer between 0-100).

**Returns:**

- Updated state with new kb value.

#### `set_scoring_formula(state, formula)`

Sets a custom scoring formula.

**Parameters:**

- `state`: The state dictionary.
- `formula`: String containing the formula using variables a, b, ka, kb.

**Returns:**

- Updated state with the new formula.

### Analysis & Output

#### `scan(state)`

Performs the analysis using the current state configuration.

**Parameters:**

- `state`: The configured state dictionary.

**Returns:**

- Updated state with analysis results.

#### `scores2html(state, output_filepath)`

Generates HTML output from analysis results.

**Parameters:**

- `state`: The state dictionary with analysis results.
- `output_filepath`: Path where the HTML output will be saved.

**Returns:**

- None (writes file to disk).

## Python API - Usage Example

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

# Set custom scoring formula (default expression provided as example)
state = aliscan.set_scoring_formula(state, "1 - (ka*0.5)*(1-a) - (kb*0.1)*b")

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

## Acknowledgements

This project is complete rewrite of the original Aliscan tool:

```
Aliscan. An interactive tool to assist the design of sequence alignment-based probes. P. De Marta, G. Firrao. Cost Action 853 - Agricultural Biomarkers for Array Technology. Wadensvill 2002.
```
