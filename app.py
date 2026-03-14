import os
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename

# Import functions from the existing generator WITHOUT modifying it
from ranklist_generator import (
    process_raw_ranklist,
    detect_score_column,
    integrate_to_template,
    FINAL_TEMPLATE_MAPPING_BASE,
    TEMPLATE_SKIP_ROWS,
    PERMANENT_TEMPLATE_FILE
)

app = Flask(__name__)

# Determine if running on Vercel
IS_VERCEL = "VERCEL" in os.environ

# The project root — files are saved here directly
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# On Vercel, use /tmp for writes. Locally, use the project dir.
BASE_DIR = "/tmp" if IS_VERCEL else PROJECT_DIR
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_file():
    if 'raw_file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['raw_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    try:
        # Form data
        custom_title    = request.form.get('custom_title', '').strip()
        custom_filename = request.form.get('custom_filename', '').strip() or 'ranklist_output'
        batches_str     = request.form.get('batches', '').strip()

        # Process raw CSV
        processed_df = process_raw_ranklist(upload_path)
        score_column = detect_score_column(processed_df)

        # ── Debug: print and log what was received ────────────────────────────
        rows_before = len(processed_df)
        available_ids = [str(b).strip() for b in processed_df['Batch ID'].fillna('').unique() if str(b).strip()]
        
        with open(os.path.join(PROJECT_DIR, 'debug_filter.log'), 'w') as f_log:
            f_log.write(f"Timestamp: {os.path.abspath(upload_path)}\n")
            f_log.write(f"Total rows before filter: {rows_before}\n")
            f_log.write(f"Received batches_str: '{batches_str}'\n")
            f_log.write(f"Available IDs in data: {sorted(available_ids)}\n")

            # ── Batch filtering ───────────────────────────────────────────────────
            valid = []
            if batches_str:
                available_lower = {bid.lower(): bid for bid in available_ids}
                requested = [b.strip() for b in batches_str.split(',') if b.strip()]
                f_log.write(f"Requested parsing: {requested}\n")
                
                for req in requested:
                    if req in available_ids:
                        valid.append(req)
                    elif req.lower() in available_lower:
                        valid.append(available_lower[req.lower()])
                
                f_log.write(f"Valid IDs matched: {valid}\n")
                
                # Apply filter
                if valid:
                    processed_df = processed_df[
                        processed_df['Batch ID'].astype(str).str.strip().isin(valid)
                    ].copy()
                else:
                    # If user requested batches but none found match, return empty to be safe
                    # rather than returning everything
                    processed_df = processed_df.iloc[0:0].copy()
            else:
                # If no batches_str provided, do not filter (keep all)
                f_log.write("No batches_str provided, skipping filter.\n")

            rows_after = len(processed_df)
            f_log.write(f"Rows after filter: {rows_after}\n")

        print(f"\n[BATCH DEBUG] {rows_before} -> {rows_after} rows. Selected: {valid}")

        # Build mapping
        mapping = FINAL_TEMPLATE_MAPPING_BASE.copy()
        mapping['Score (60)'] = score_column

        # Save output to our designated output directory
        integrate_to_template(
            processed_df=processed_df,
            template_path=PERMANENT_TEMPLATE_FILE,
            mapping=mapping,
            skip_rows=TEMPLATE_SKIP_ROWS,
            custom_title=custom_title,
            out_base_name=custom_filename,
            out_dir=OUTPUT_DIR,
            make_pdf=True
        )

        # Collect generated files from OUTPUT_DIR
        generated = []
        for ext in ['xlsx', 'csv', 'pdf']:
            path = os.path.join(OUTPUT_DIR, f"{custom_filename}.{ext}")
            if os.path.exists(path):
                generated.append({'name': f"{custom_filename}.{ext}", 'ext': ext})

        return jsonify({
            'success': True,
            'files': generated,
            'output_dir': OUTPUT_DIR,
            'debug': {
                'received_batches': batches_str,
                'valid_batches': valid,
                'rows_before': rows_before,
                'rows_after': rows_after,
            }
        })

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        print(f"\n🛑 [ERROR] 500 INTERNAL SERVER ERROR:\n{tb_str}")
        return jsonify({'error': str(e), 'traceback': tb_str}), 500

    finally:
        if os.path.exists(upload_path):
            try:
                os.remove(upload_path)
            except:
                pass


@app.route('/download/<path:filename>')
def download_file(filename):
    """Serve a generated file from the project directory for download."""
    safe_name = os.path.basename(filename)
    file_path = os.path.join(OUTPUT_DIR, safe_name)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True, download_name=safe_name)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
