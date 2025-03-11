#!/usr/bin/env python3
# signs.py
# Functions for sequence alignment scanning
# author email: patrick.demarta@gmail.com

import csv
import sys
import os
from Bio import SeqIO

def create_state():
    """Create an initial state dictionary with default values"""
    return {
        "alignment": [],
        "num_of_seqs": 0,
        "seq_size": 0,
        "groups": [],
        "ka": 20,
        "kb": 20,
        "scoring_formula": "1 - (ka*0.5)*(1-a) - (kb*0.1)*b",
        "score_color_ranges": [0.5, 0.7, 0.8, 0.9],
        "paging_window_lenght": 120,  # Changed from 80 to 120 bases per line
        "label_size": 20,
        "scores": [],
        "input_filename": "",
        "output_mode": "html"  # Can be 'html' or 'text'
    }

def load_alignment(state, infile, *group_defs):
    """
    Load a fasta format multiple sequence alignment file
    Required: fasta format multiple sequence alignment filename  
    Optional: groups definition as comma separated list of arrays and/or ranges
    """
    state = state.copy()
    
    state["input_filename"] = infile
    state["alignment"] = create_alignment(infile)
    state["num_of_seqs"] = len(state["alignment"])
    state["seq_size"] = len(state["alignment"][0].seq)
    state["groups"] = sanitize(state["alignment"], group_defs)
    state["scores"] = []
    
    return state

def create_alignment(filename):
    """Import a fasta multiple sequences file into a list of SeqRecord objects"""
    alignment_data = []
    with open(filename) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            alignment_data.append(record)
    return alignment_data

def sanitize(alignment_data, groups_def):
    """
    Generate a list of sequence-indexes' lists,
    puts each sequence index in a single group-list if groups_def is empty
    """
    sanitized_groups = []
    if not groups_def:
        for seq_index in range(len(alignment_data)):
            sanitized_groups.append([seq_index])
    else:
        for group in groups_def:
            if isinstance(group, range):
                sanitized_groups.append(list(group))
            else:
                sanitized_groups.append(list(group))
    return sanitized_groups

def scan(state):
    """
    Iterate along nt positions, calculate nt frequencies for ingroup and outgroups, calculate nt score
    """
    state = state.copy()
    
    # Create a copy of groups to avoid modifying original
    groups_copy = [group.copy() for group in state["groups"]]
    
    state["scores"] = reset_scores(state)
    sequence_length_range = range(state["seq_size"])
    
    for position in sequence_length_range:
        for _ in range(len(groups_copy)):
            ingroup = groups_copy.pop(0)
            outgroup = []
            for group in groups_copy:
                outgroup.extend(group)
            groups_copy.append(ingroup)
            
            ingroup_frequencies = calculate_nt_freq(state, ingroup, position)
            outgroup_frequencies = calculate_nt_freq(state, outgroup, position)
            state = calculate_score(state, ingroup, position, ingroup_frequencies, outgroup_frequencies)
    
    return state

def reset_scores(state):
    """Create a new scores list of num_of_seqs empty lists"""
    return [[] for _ in range(state["num_of_seqs"])]

def calculate_nt_freq(state, group, position):
    """Calculate (a,c,t,g,-) frequencies at current position in group"""
    num_of_seqs_in_group = len(group)
    a = c = t = g = gap = 0
    
    for seq_id in group:
        base_val = get_base(state, seq_id, position)
        if base_val == "A":
            a += 1
        elif base_val == "C":
            c += 1
        elif base_val == "T":
            t += 1
        elif base_val == "G":
            g += 1
        elif base_val == "-":
            gap += 1
    
    return {
        "fA": a / num_of_seqs_in_group,
        "fT": t / num_of_seqs_in_group,
        "fC": c / num_of_seqs_in_group,
        "fG": g / num_of_seqs_in_group,
        "fgap": gap / num_of_seqs_in_group
    }

def calculate_score(state, ingroup, position, ingroup_frequencies, outgroup_frequencies):
    """
    Set the current base frequencies values on a (consensus) and b (aspecificity)
    evaluate the scoring formula and stores the score
    """
    state = state.copy()
    scores_copy = [score.copy() for score in state["scores"]]
    
    for seq_id in ingroup:
        base_val = get_base(state, seq_id, position)
        a = b = 0
        
        if base_val == "A":
            a = ingroup_frequencies["fA"]
            b = outgroup_frequencies["fA"]
        elif base_val == "C":
            a = ingroup_frequencies["fC"]
            b = outgroup_frequencies["fC"]
        elif base_val == "T":
            a = ingroup_frequencies["fT"]
            b = outgroup_frequencies["fT"]
        elif base_val == "G":
            a = ingroup_frequencies["fG"]
            b = outgroup_frequencies["fG"]
        elif base_val == "-":
            a = ingroup_frequencies["fgap"]
            b = outgroup_frequencies["fgap"]
        
        # Use local variables in place of globals
        ka = state["ka"]
        kb = state["kb"]
        
        # Evaluate the scoring formula
        score = eval(state["scoring_formula"])
        scores_copy[seq_id].append(score)
    
    state["scores"] = scores_copy
    return state

def color_mask_score(state, base, nt_score):
    """Color masking according to the base score using HTML styling"""
    ranges = state["score_color_ranges"]
    if nt_score < ranges[0]:
        return f'<span style="color:black;">{base}</span>'  # Changed from blue to black
    elif nt_score >= ranges[0] and nt_score < ranges[1]:
        return f'<span style="background-color:blue;color:white;">{base}</span>'
    elif nt_score >= ranges[1] and nt_score < ranges[2]:
        return f'<span style="background-color:green;color:white;">{base}</span>'
    elif nt_score >= ranges[2] and nt_score < ranges[3]:
        return f'<span style="background-color:yellow;color:black;">{base}</span>'
    elif nt_score >= ranges[3]:
        return f'<span style="background-color:red;color:white;">{base}</span>'

def color_ruler(state):
    """Create an HTML ruler for the color guide"""
    ranges = state["score_color_ranges"]
    ruler = f'<span style="color:black;">| &lt; {ranges[0]} </span>'
    ruler += f'<span style="background-color:blue;color:white;">| .. {ranges[1]} </span>'
    ruler += f'<span style="background-color:green;color:white;">| .. {ranges[2]} </span>'
    ruler += f'<span style="background-color:yellow;color:black;">| .. {ranges[3]} </span>'
    ruler += f'<span style="background-color:red;color:white;">| &gt; {ranges[3]} |</span>'
    return ruler

def print_scores(state):
    """Creates and prints HTML-formatted alignment with color masking"""
    if state["output_mode"] == "html":
        html_output = scores_to_html(state)
        print(html_output)
        return html_output
    else:
        print("Text output mode is not supported without colorama")
        return False

def scores_to_html(state):
    """Convert the scores to HTML-formatted alignment"""
    html = ['<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Alignment Visualization</title>',
            '<style>',
            'body { font-family: monospace; }',
            '.group { position: relative; }',
            '.group-header { font-weight: bold; color: #4a4a9c; position: absolute; left: 0; width: 100px; text-align: left; padding-right: 30px; }', # Increased padding, kept original width
            '.ruler { color: #9c4a4a; margin-left: 100px; margin-bottom: 10px; }',  # Back to original margin
            '.page-header { font-weight: bold; margin-top: 15px; }',
            '.page-container { margin-top: 20px; }',
            '.sequence { white-space: pre; margin-left: 100px; }',  # Back to original margin
            '.label { color: black; display: inline-block; width: ' + str(state["label_size"]) + 'ch; }',
            '.first-sequence { margin-top: 0; }',
            '.non-first-sequence { margin-top: 0; }',
            '</style>',
            '</head>',
            '<body>',
            '<h1>Alignment Visualization</h1>',
            '<div>File: ' + state["input_filename"] + '</div>',
            '<div style="margin-left: 100px;">' + color_ruler(state) + '</div>']
    
    paged_aln = paging(state)
    for page_number, alignment_window in enumerate(paged_aln):
        # Page header and single ruler per page
        html.append(f'<div class="page-container">')
        html.append(f'<div class="page-header">Page #{page_number+1}</div>')
        html.append(f'<div class="ruler">{page_ruler_html(state, page_number)}</div>')
        
        for group_index, group in enumerate(state["groups"]):
            html.append(f'<div class="group">')
            # Group header will be displayed to the left of the first sequence
            html.append(f'<div class="group-header">Group {group_index}</div>')
            
            for seq_index, seq_id in enumerate(group):
                if seq_id < len(alignment_window):
                    paged_seq = alignment_window[seq_id]
                    
                    # Add a class to differentiate the first sequence from others
                    seq_class = "first-sequence" if seq_index == 0 else "non-first-sequence"
                    
                    # Create the sequence HTML as a single string
                    sequence_html = f'<div class="sequence {seq_class}">'
                    sequence_html += format_label_html(state, seq_id)
                    
                    # Build the colored bases as a single string
                    for i, base_char in enumerate(paged_seq):
                        position = i + state["paging_window_lenght"] * page_number
                        if position < state["seq_size"]:
                            base_val = get_base(state, seq_id, position)
                            nt_score = state["scores"][seq_id][position]
                            sequence_html += color_mask_score(state, base_val, nt_score)
                    
                    sequence_html += '</div>'
                    html.append(sequence_html)
            
            html.append('</div>')
        
        # Close page container div
        html.append('</div>')
    
    html.append('</body>')
    html.append('</html>')
    
    return '\n'.join(html)

def page_ruler_html(state, page_number):
    """Create the HTML sequence ruler for the current window-page"""
    ruler = "&nbsp;" * state["label_size"]
    pos = 1
    for _ in range(state["paging_window_lenght"]):
        if pos % 10 == 0:
            ruler += "|"
        else:
            ruler += "-"
        pos += 1
    ruler += str(state["paging_window_lenght"] + page_number * state["paging_window_lenght"])
    return f'<span style="color:purple;">{ruler}</span>'

def format_label_html(state, seq_id):
    """Format seq labels to label_size chars length with HTML"""
    definition = f"{seq_id}. {state['alignment'][seq_id].description}"
    if len(definition) <= state["label_size"]:
        label = definition + "&nbsp;" * (state["label_size"] - len(definition))
    else:
        label = definition[:state["label_size"]]
    return f'<span class="label">{label}</span>'

def paging(state):
    """Set the paging windows for the alignment"""
    num_of_windows = (state["seq_size"] // state["paging_window_lenght"]) + 1
    paged_aln = []
    
    for window in range(num_of_windows):
        alignment_window = []
        for seq_id, sequence in enumerate(state["alignment"]):
            window_start = state["paging_window_lenght"] * window
            window_stop = (state["paging_window_lenght"] * window) + state["paging_window_lenght"]
            window_stop = min(window_stop, state["seq_size"])
            alignment_window.append(str(sequence.seq[window_start:window_stop]))
        paged_aln.append(alignment_window)
    
    return paged_aln

def get_base(state, seq_id, position):
    """Return the uppercase base given seq_id and position"""
    return str(state["alignment"][seq_id].seq[position]).upper()

def scores2csv(state, outfile):
    """Write the scores in a csv outfile"""
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for seq_index, seq_score in enumerate(state["scores"]):
            definition = state["alignment"][seq_index].description
            writer.writerow([definition] + seq_score)


def set_ka(state, value):
    """Set the ka parameter (consensus coefficient)"""
    state = state.copy()
    state["ka"] = value
    return state
    
def set_kb(state, value):
    """Set the kb parameter (aspecificity tolerance coefficient)"""
    state = state.copy()
    state["kb"] = value
    return state

def set_groups(state, group_list):
    """Set the groups of sequences"""
    state = state.copy()
    state["groups"] = group_list  # Simply assign the group_list directly
    return state
    
def set_scoring_formula(state, formula):
    """Set the scoring formula"""
    state = state.copy()
    state["scoring_formula"] = formula
    return state
    
def set_color_ranges(state, ranges):
    """Set the color ranges for scoring"""
    state = state.copy()
    if len(ranges) == 4:
        state["score_color_ranges"] = list(ranges)
    return state

def scores2html(state, outfile="alignment.html"):
    """Write the HTML color-masked alignment to a file"""
    html_content = scores_to_html(state)
    
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML output written to '{outfile}'")
    return outfile

# Example of how to use the functions:
def run_example(fasta_file, outfile="results.html"):
    """Example of how to use this module with HTML output"""
    # Initialize state
    state = create_state()
    
    # Load alignment
    state = load_alignment(state, fasta_file)
    
    # Set groups
    state = set_groups(state, [[0, 1, 2], [3, 4, 5]])
    
    # Set parameters
    state = set_ka(state, 10)
    state = set_kb(state, 10)
    
    # Run scan
    state = scan(state)
    
    # Generate and save HTML output
    scores2html(state, outfile)
    
    return state