#!/usr/bin/env python3
# Web interface for aliscan
# author email: patrick.demarta@gmail.com

from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
import aliscan

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alignment_scanner_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global state dictionary to store current alignment data
current_state = None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_state
    
    if 'alignment_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
        
    file = request.files['alignment_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
        
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Initialize our state
            current_state = aliscan.create_state()
            current_state = aliscan.load_alignment(current_state, file_path)
            
            # Get sequence information for display
            sequences = []
            for idx, record in enumerate(current_state["alignment"]):
                sequences.append({
                    'id': idx,
                    'description': record.description
                })
                
            return render_template('configure.html', 
                                  sequences=sequences, 
                                  filename=filename)
                                  
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(request.url)

@app.route('/run_scan', methods=['POST'])
def run_scan():
    global current_state
    
    if current_state is None:
        flash('Please upload an alignment file first')
        return redirect(url_for('index'))
    
    try:
        # Parse groups from form
        group_count = int(request.form.get('group_count', 0))
        groups = []
        
        for i in range(group_count):
            group_key = f'group_{i}'
            if group_key in request.form:
                # Convert selected sequence IDs to integers
                seq_ids = [int(seq_id) for seq_id in request.form.getlist(group_key)]
                if seq_ids:
                    groups.append(seq_ids)
        
        # Set parameters
        ka = float(request.form.get('ka', 20))
        kb = float(request.form.get('kb', 20))
        
        # Update state with user selections
        if groups:
            current_state = aliscan.set_groups(current_state, groups)
        current_state = aliscan.set_ka(current_state, ka)
        current_state = aliscan.set_kb(current_state, kb)
        
        # Run the scan
        current_state = aliscan.scan(current_state)
        
        # Generate HTML output
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'results.html')
        aliscan.scores2html(current_state, results_file)
        
        # Pass the HTML content to the template
        with open(results_file, 'r') as f:
            html_content = f.read()
            
        return render_template('results.html', 
                              html_content=html_content,
                              ka=ka,
                              kb=kb,
                              groups=groups)
        
    except Exception as e:
        flash(f'Error running scan: {str(e)}')
        return redirect(url_for('index'))

@app.route('/update_parameters', methods=['POST'])
def update_parameters():
    global current_state
    
    if current_state is None:
        flash('Session expired. Please upload a file and configure the analysis again.')
        return redirect(url_for('index'))
    
    try:
        # Get updated parameters
        ka = float(request.form.get('ka', 20))
        kb = float(request.form.get('kb', 20))
        
        # Update state with new parameters
        current_state = aliscan.set_ka(current_state, ka)
        current_state = aliscan.set_kb(current_state, kb)
        
        # Re-run the scan
        current_state = aliscan.scan(current_state)
        
        # Generate updated HTML output
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'results.html')
        aliscan.scores2html(current_state, results_file)
        
        # Read the updated HTML content
        with open(results_file, 'r') as f:
            html_content = f.read()
        
        # Keep the original groups for display
        groups = current_state["groups"]
            
        return render_template('results.html', 
                              html_content=html_content,
                              ka=ka,
                              kb=kb,
                              groups=groups)
        
    except Exception as e:
        flash(f'Error updating parameters: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download_results')
def download_results():
    results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'results.html')
    if os.path.exists(results_file):
        return send_file(results_file, as_attachment=True, download_name="alignment_results.html")
    else:
        flash('No results file found')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
