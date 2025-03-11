# aliscan (v1.0)

## Overview

Aliscan is a tool for analyzing nucleotide sequence alignments to identify signature patterns. It provides a web interface for uploading, configuring, and visualizing sequence alignments with color-coded scoring based on nucleotide position significance.

## Features

- **Web Interface**: Upload and analyze alignment files through a user-friendly web interface
- **Group-Based Analysis**: Create custom sequence groups for comparative analysis
- **Configurable Parameters**: Adjust scoring parameters for consensus (ka) and aspecificity (kb)
- **Visual Results**: Color-masked alignment visualization with score highlighting
- **Downloadable Results**: Export analysis results in HTML format

## Requirements

- **Python 3.6 or higher**: Core programming language used for the application
- **Flask 2.2.3**: Web framework for building the application's interface
- **Werkzeug 2.2.3**: WSGI utility library for handling HTTP requests and serving the web application
- **BioPython 1.81**: Library for biological computation, used for processing and analyzing nucleotide sequences

## Installation

### Clone the repository

```bash
git clone https://github.com/username/aliscan.git
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

- **kb (Aspecificity tolerance)**:
  - 20: Forbid appearance in outgroup
  - 10: Penalize appearance in outgroup

### Scoring Formula

The scoring formula used is: `1 - (ka*0.5)*(1-a) - (kb*0.1)*b`

Where:

- **a**: frequency of the nucleotide in the ingroup (consensus)
- **b**: frequency of the nucleotide in the outgroup (aspecificity)
- **ka**: consensus coefficient
- **kb**: aspecificity tolerance coefficient

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

## Color Coding

The output alignment is color-coded based on the calculated scores:

- **Black**: Score < 0.5
- **Blue**: Score between 0.5 and 0.7
- **Green**: Score between 0.7 and 0.8
- **Yellow**: Score between 0.8 and 0.9
- **Red**: Score > 0.9

## File Format Support

Aliscan accepts FASTA format multiple sequence alignment files (.fasta, .fa, .aln).

## Contributing

Contributions to improve aliscan are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Author: Patrick De Marta  
Email: patrick.demarta@gmail.com
