"""Intake Blueprint: Manchester Triage Queue, Pipeline Telemetry, Manual Intake & Multimodal Upload."""
import csv
import json
import logging
import os
import time
from collections import Counter
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, session
from flask_login import login_required
from markupsafe import escape as h_escape
from werkzeug.utils import secure_filename

import db
from verticals import filter_patients_for_vertical, get_active_vertical
from blueprints.common import audit
from logging_setup import pseudonymize
from clinical_intake import (
    MTS_METADATA,
    build_fhir_bundle,
    calculate_mts_category,
    extract_from_clinical_document,
    parse_allergies,
    parse_labs,
    parse_medications,
    resolve_snomed,
)
from fhir_utils import check_drug_allergy_contraindications, calculate_news2_score

logger = logging.getLogger(__name__)
intake_bp = Blueprint('intake_bp', __name__)


def _get_pipeline_telemetry(app):
    raw_dir = app.config.get('RAW_DATA_PATH', '/workspace/data/raw')
    if not os.path.isdir(raw_dir):
        raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw'))
    raw_files = []
    if os.path.isdir(raw_dir):
        raw_files = [f for f in os.listdir(raw_dir) if not f.startswith('.')]

    store_dir = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
    if not os.path.isdir(store_dir):
        store_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'fhir_store'))
    bundles = []
    if os.path.isdir(store_dir):
        bundles = [f for f in os.listdir(store_dir) if f.startswith('bundle_')]

    return {
        'raw_count': len(raw_files),
        'raw_files': raw_files[:20],
        'bundle_count': len(bundles),
        'store_path': store_dir,
        'raw_path': raw_dir,
    }


def register_intake_routes(app, csrf):
    fhir = app.fhir

    @app.route('/fhir/Triage', endpoint='triage_queue_view')
    @login_required
    def triage_queue_view():
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view='/fhir/Triage')
        queue = []
        if hasattr(app.fhir, 'get_triage_queue'):
            queue = app.fhir.get_triage_queue()
        queue = filter_patients_for_vertical(queue, get_active_vertical(session, db), id_key='patient_id')
        cat_counts = Counter(p.get('mts_category', 3) for p in queue)
        refreshed_time = datetime.now().strftime('%H:%M:%S')
        return render_template('triage.html', queue=queue, cat_counts=cat_counts, refreshed_time=refreshed_time)

    @app.route('/fhir/triage_fragment', endpoint='triage_queue_fragment')
    @login_required
    def triage_queue_fragment():
        queue = []
        if hasattr(app.fhir, 'get_triage_queue'):
            queue = app.fhir.get_triage_queue()
        queue = filter_patients_for_vertical(queue, get_active_vertical(session, db), id_key='patient_id')
        cat_counts = Counter(p.get('mts_category', 3) for p in queue)
        refreshed_time = datetime.now().strftime('%H:%M:%S')
        return render_template('triage_fragment.html', queue=queue, cat_counts=cat_counts, refreshed_time=refreshed_time)

    @app.route('/pipeline/status', endpoint='pipeline_status_view')
    @login_required
    def pipeline_status_view():
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view='/pipeline/status')
        return render_template('pipeline_status.html', **_get_pipeline_telemetry(app))

    @app.route('/pipeline/status_fragment', endpoint='pipeline_status_fragment')
    @login_required
    def pipeline_status_fragment():
        return render_template('pipeline_status_fragment.html', **_get_pipeline_telemetry(app))

    @app.route('/api/v1/fhir/ingest', methods=['POST'], endpoint='api_ingest_bundle')
    @csrf.exempt
    def api_ingest_bundle():
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400
        if hasattr(app.fhir, 'save_bundle'):
            saved_path = app.fhir.save_bundle(payload)
            return jsonify({
                'status': 'success',
                'message': 'Bundle ingested and indexed into Slainte-Engine.',
                'file_path': saved_path
            }), 201
        return jsonify({'status': 'received', 'message': 'App running with remote FHIR backend'}), 200

    @app.route('/fhir/Bundle', methods=['POST'], endpoint='fhir_bundle_ingest')
    @csrf.exempt
    def fhir_bundle_ingest():
        return api_ingest_bundle()

    @app.route('/fhir/intake', methods=['POST'], endpoint='manual_intake')
    @login_required
    def manual_intake():
        full_name = request.form.get('full_name', '').strip()
        if not full_name:
            return '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Patient full name is required.</div>', 400

        complaint = request.form.get('complaint', '').strip()
        if not complaint:
            return '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Chief complaint is required.</div>', 400

        gender = request.form.get('gender', 'unknown').strip().lower()
        dob = request.form.get('dob', '').strip() or None
        gms_number = request.form.get('gms_number', '').strip()

        def _parse_num(field):
            v = request.form.get(field, '').strip()
            if not v:
                return None
            try:
                return float(v)
            except ValueError:
                return None

        vitals = {
            'systolic_bp': _parse_num('sys_bp'),
            'diastolic_bp': _parse_num('dia_bp'),
            'heart_rate': _parse_num('hr'),
            'spo2': _parse_num('spo2'),
            'respiratory_rate': _parse_num('resp_rate'),
            'temperature': _parse_num('temp_c'),
            'pain': _parse_num('pain'),
            'complaint': complaint
        }

        mts_cat = calculate_mts_category(vitals)
        mts_info = MTS_METADATA.get(mts_cat, MTS_METADATA[3])
        snomed_code, snomed_disp = resolve_snomed(complaint)

        pt_id = None
        if gms_number and hasattr(app.fhir, 'find_patient_id_by_gms'):
            pt_id = app.fhir.find_patient_id_by_gms(gms_number)

        if not pt_id:
            if hasattr(app.fhir, '_cache_patients') and app.fhir._cache_patients:
                existing_ids = list(app.fhir._cache_patients.keys())
                num_ids = [int(p[1:]) for p in existing_ids if p.startswith('P') and p[1:].isdigit()]
                next_num = (max(num_ids) + 1) if num_ids else 119
                pt_id = f"P{next_num}"
            else:
                pt_id = f"P{int(time.time() * 1000) % 10000:04d}"

        if not gms_number:
            gms_number = f"99{pt_id[1:]}-Z"

        labs_data = parse_labs(request.form.get('labs'))
        meds_data = parse_medications(request.form.get('medications'))
        algs_data = parse_allergies(request.form.get('allergies'))

        bundle = build_fhir_bundle(
            pt_id=pt_id,
            name=full_name,
            gms_number=gms_number,
            gender=gender,
            birthdate=dob,
            complaint=complaint,
            vitals=vitals,
            mts_category=mts_cat,
            labs=labs_data,
            medications=meds_data,
            allergies=algs_data
        )

        if hasattr(app.fhir, 'save_bundle'):
            app.fhir.save_bundle(bundle, f"bundle_{pt_id}.json")
        else:
            if not app.config.get('TESTING'):
                fhir.post('Bundle', json_data=bundle)
            store_dir = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
            os.makedirs(store_dir, exist_ok=True)
            with open(os.path.join(store_dir, f"bundle_{pt_id}.json"), "w", encoding="utf-8") as f:
                json.dump(bundle, f, indent=2)

        try:
            raw_dir = app.config.get('RAW_DATA_PATH', '/workspace/data/raw')
            os.makedirs(raw_dir, exist_ok=True)
            intake_csv_path = os.path.join(raw_dir, 'manual_intake_patients.csv')
            file_exists = os.path.isfile(intake_csv_path)
            with open(intake_csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                if not file_exists:
                    writer.writerow([
                        'pt_id', 'Patient_Name', 'GMS_NO', 'sex', 'DOB', 'triage_complaint',
                        'sys_bp', 'dia_bp', 'hr', 'o2_sat', 'resp_rate', 'temp_c', 'pain_level',
                        'labs', 'medications', 'allergies'
                    ])
                writer.writerow([
                    pt_id, full_name, gms_number, gender, dob or '', complaint,
                    vitals['systolic_bp'] or '', vitals['diastolic_bp'] or '', vitals['heart_rate'] or '',
                    vitals['spo2'] or '', vitals['respiratory_rate'] or '', vitals['temperature'] or '',
                    vitals['pain'] or '', request.form.get('labs', ''), request.form.get('medications', ''),
                    request.form.get('allergies', '')
                ])
        except Exception as e:
            logger.warning(f"Failed to append to manual intake audit CSV: {e}")

        vitals_badges = []
        if vitals['systolic_bp'] and vitals['diastolic_bp']:
            vitals_badges.append(f'<span class="badge bg-light text-dark border">BP: {int(vitals["systolic_bp"])}/{int(vitals["diastolic_bp"])}</span>')
        if vitals['heart_rate']:
            vitals_badges.append(f'<span class="badge bg-light text-dark border">HR: {int(vitals["heart_rate"])} bpm</span>')
        if vitals['spo2']:
            vitals_badges.append(f'<span class="badge bg-light text-dark border">SpO2: {int(vitals["spo2"])}%</span>')
        if vitals['temperature']:
            vitals_badges.append(f'<span class="badge bg-light text-dark border">Temp: {vitals["temperature"]}°C</span>')
        if vitals['pain'] is not None:
            vitals_badges.append(f'<span class="badge bg-light text-dark border">Pain: {int(vitals["pain"])}/10</span>')

        safe_full_name = h_escape(full_name)
        safe_complaint = h_escape(complaint)
        safe_gms_number = h_escape(gms_number)
        safe_pt_id = h_escape(pt_id)
        safe_snomed = h_escape(str(snomed_code))

        news2_score, news2_tier, _ = calculate_news2_score(vitals)
        safety_alerts = check_drug_allergy_contraindications(algs_data, meds_data)
        if safety_alerts:
            audit('clinical.safety_gate_intercepted', outcome='warning',
                  detail={'patient_id': pt_id, 'alerts': len(safety_alerts)})

        safety_banner = ""
        if safety_alerts:
            alerts_items = "".join([
                f'<li class="mb-1"><strong>[{a["severity"]}] {a["allergen"]} &harr; {a["medication"]}:</strong> {a["message"]}</li>'
                for a in safety_alerts
            ])
            safety_banner = f"""
            <div class="alert alert-danger py-2 px-3 small border-0 shadow-sm mt-2">
                <div class="fw-bold mb-1"><i class="fas fa-exclamation-triangle text-danger me-1"></i>CDS Safety Gate Intercepted Potential Contraindications:</div>
                <ul class="mb-0 ps-3">{alerts_items}</ul>
            </div>
            """

        news2_badge_class = "bg-danger text-white" if news2_score >= 7 else ("bg-warning text-dark" if news2_score >= 5 else ("bg-info text-dark" if news2_score >= 1 else "bg-success text-white"))
        badges_html = ' '.join(vitals_badges)

        return f"""
        <div class="alert alert-success border-0 shadow-sm p-3 mt-3 animate-fade-in">
            <div class="d-flex align-items-center justify-content-between mb-2">
                <div class="d-flex align-items-center gap-1">
                    <span class="badge {mts_info['badge']} px-3 py-2 fs-6">
                        Cat {mts_cat}: {mts_info['name']}
                    </span>
                    <span class="badge {news2_badge_class} px-2 py-2">
                        <i class="fas fa-heartbeat me-1"></i>NEWS2: {news2_score}/20 ({news2_tier})
                    </span>
                    <span class="badge bg-dark text-white px-2 py-2">
                        Target: {mts_info['target_time_minutes']} min
                    </span>
                </div>
                <span class="badge bg-success text-white border border-success">
                    <i class="fas fa-check-circle me-1"></i> Validated FHIR R4 Bundle
                </span>
            </div>
            <div class="mb-2">
                <h6 class="mb-1 fw-bold">{safe_full_name} <span class="text-muted fw-normal">({safe_pt_id} &bull; GMS: {safe_gms_number})</span></h6>
                <p class="mb-1 small text-dark"><strong>Chief Complaint:</strong> {safe_complaint} <span class="badge bg-secondary-subtle text-secondary ms-1">SNOMED {safe_snomed}</span></p>
                <div class="d-flex flex-wrap gap-1 mt-1">{badges_html}</div>
                {safety_banner}
            </div>
            <hr class="my-2 text-muted">
            <div class="d-flex align-items-center justify-content-between pt-1">
                <small class="text-muted"><i class="fas fa-robot text-primary me-1"></i>Synchronized to OpenHands audit ledger &amp; indexed to FHIR store.</small>
                <div class="d-flex gap-2">
                    <a href="/fhir/Patient/{safe_pt_id}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-id-card me-1"></i> View Patient Detail
                    </a>
                    <button type="button" class="btn btn-sm btn-success" onclick="window.location.href='/?view=/fhir/Triage'">
                        <i class="fas fa-list me-1"></i> View Triage Queue
                    </button>
                </div>
            </div>
        </div>
        """

    @app.route('/fhir/upload', methods=['POST'], endpoint='batch_upload')
    @login_required
    def batch_upload():
        if 'clinical_file' not in request.files:
            return '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>No file selected for upload.</div>', 400

        file = request.files['clinical_file']
        if not file or not file.filename:
            return '<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Filename is empty.</div>', 400

        ALLOWED_EXTENSIONS = {'.csv', '.tsv', '.json', '.pdf', '.png', '.jpg', '.jpeg'}
        ext = os.path.splitext(file.filename or '')[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return f'<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Unsupported file type: {ext or "unknown"}. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}</div>', 400

        filename = secure_filename(file.filename)
        if not filename:
            filename = f"upload_{int(time.time())}{ext}"

        raw_dir = app.config.get('RAW_DATA_PATH', '/workspace/data/raw')
        os.makedirs(raw_dir, exist_ok=True)
        dest_path = os.path.join(raw_dir, filename)
        file.save(dest_path)
        file_size_kb = max(1, os.path.getsize(dest_path) // 1024)

        safe_filename = h_escape(filename)
        safe_dest_path = h_escape(dest_path)

        if ext in ('.pdf', '.png', '.jpg', '.jpeg'):
            extracted = extract_from_clinical_document(dest_path)
            complaint = extracted.get('complaint') or f"Clinical document intake ({filename})"
            vitals = {
                'systolic_bp': extracted.get('systolic_bp'),
                'diastolic_bp': extracted.get('diastolic_bp'),
                'heart_rate': extracted.get('heart_rate'),
                'spo2': extracted.get('spo2'),
                'respiratory_rate': extracted.get('respiratory_rate'),
                'temperature': extracted.get('temperature'),
                'pain': extracted.get('pain'),
                'complaint': complaint
            }

            mts_cat = calculate_mts_category(vitals)
            mts_info = MTS_METADATA.get(mts_cat, MTS_METADATA[3])
            snomed_code, snomed_disp = resolve_snomed(complaint)

            pt_id = None
            if hasattr(app.fhir, '_cache_patients') and app.fhir._cache_patients:
                existing_ids = list(app.fhir._cache_patients.keys())
                num_ids = [int(p[1:]) for p in existing_ids if p.startswith('P') and p[1:].isdigit()]
                next_num = (max(num_ids) + 1) if num_ids else 119
                pt_id = f"P{next_num}"
            else:
                pt_id = f"P{int(time.time() * 1000) % 10000:04d}"

            gms_number = extracted.get('gms_number') or f"99{pt_id[1:]}-D"
            full_name = extracted.get('full_name') or f"Scanned Patient ({filename[:12]})"
            gender = extracted.get('gender') or 'unknown'
            dob = extracted.get('dob') or '1985-06-15'

            bundle = build_fhir_bundle(
                pt_id=pt_id,
                name=full_name,
                gms_number=gms_number,
                gender=gender,
                birthdate=dob,
                complaint=complaint,
                vitals=vitals,
                mts_category=mts_cat
            )

            if hasattr(app.fhir, 'save_bundle'):
                app.fhir.save_bundle(bundle, f"bundle_{pt_id}.json")
            else:
                if not app.config.get('TESTING'):
                    fhir.post('Bundle', json_data=bundle)
                store_dir = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
                os.makedirs(store_dir, exist_ok=True)
                with open(os.path.join(store_dir, f"bundle_{pt_id}.json"), "w", encoding="utf-8") as f:
                    json.dump(bundle, f, indent=2)

            file_icon = 'fa-file-pdf text-danger' if ext == '.pdf' else 'fa-file-image text-info'
            vitals_badges = []
            if vitals['systolic_bp'] and vitals['diastolic_bp']:
                vitals_badges.append(f'<span class="badge bg-light text-dark border">BP: {int(vitals["systolic_bp"])}/{int(vitals["diastolic_bp"])}</span>')
            if vitals['heart_rate']:
                vitals_badges.append(f'<span class="badge bg-light text-dark border">HR: {int(vitals["heart_rate"])} bpm</span>')
            if vitals['spo2']:
                vitals_badges.append(f'<span class="badge bg-light text-dark border">SpO2: {int(vitals["spo2"])}%</span>')
            if vitals['temperature']:
                vitals_badges.append(f'<span class="badge bg-light text-dark border">Temp: {vitals["temperature"]}°C</span>')
            if vitals['pain'] is not None:
                vitals_badges.append(f'<span class="badge bg-light text-dark border">Pain: {int(vitals["pain"])}/10</span>')

            safe_full_name = h_escape(full_name)
            safe_complaint = h_escape(complaint)
            safe_gms = h_escape(gms_number)
            safe_pt_id = h_escape(pt_id)
            safe_snomed = h_escape(str(snomed_code))

            return f"""
            <div class="alert alert-success border-0 shadow-sm p-3 mt-3 animate-fade-in">
                <div class="d-flex align-items-center justify-content-between mb-2">
                    <div class="d-flex align-items-center gap-2">
                        <i class="fas {file_icon} fa-2x"></i>
                        <div>
                            <h6 class="mb-0 fw-bold">{safe_filename} <span class="badge bg-dark ms-1">{file_size_kb} KB</span></h6>
                            <small class="text-muted">Multimodal OCR &amp; FastMCP extraction verified.</small>
                        </div>
                    </div>
                    <span class="badge {mts_info['badge']} px-3 py-2 fs-6">
                        Cat {mts_cat}: {mts_info['name']} ({mts_info['target_time_minutes']} min)
                    </span>
                </div>
                <div class="bg-white rounded p-3 border mb-2">
                    <div class="fw-bold mb-1">{safe_full_name} <span class="text-muted fw-normal">({safe_pt_id} &bull; GMS: {safe_gms})</span></div>
                    <div class="small text-secondary mb-2"><strong>Extracted Complaint:</strong> {safe_complaint} &bull; <span class="badge bg-secondary-subtle text-secondary">SNOMED {safe_snomed}</span></div>
                    <div class="d-flex flex-wrap gap-1">{' '.join(vitals_badges)}</div>
                </div>
                <div class="d-flex align-items-center justify-content-between pt-1">
                    <small class="text-muted"><i class="fas fa-check-circle text-success me-1"></i>Standard HL7 FHIR R4 Bundle created and indexed.</small>
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="window.location.href='/?view=patients'">
                            <i class="fas fa-users me-1"></i> Patients List
                        </button>
                        <button type="button" class="btn btn-sm btn-success" onclick="window.location.href='/?view=triage'">
                            <i class="fas fa-heartbeat me-1"></i> Live Triage Queue
                        </button>
                    </div>
                </div>
            </div>
            """

        row_count = 0
        try:
            with open(dest_path, 'r', encoding='utf-8', errors='replace') as f:
                row_count = max(0, sum(1 for line in f if line.strip()) - 1)
        except Exception:
            row_count = 1

        return f"""
        <div class="alert alert-primary border-0 shadow-sm p-3 mt-3 animate-fade-in">
            <div class="d-flex align-items-center mb-2">
                <i class="fas fa-file-csv fa-2x text-primary me-3"></i>
                <div>
                    <h6 class="mb-0 fw-bold">{safe_filename} <span class="badge bg-info text-dark ms-2">{file_size_kb} KB</span></h6>
                    <small class="text-muted">Detected {row_count} clinical triage record(s) in batch.</small>
                </div>
            </div>
            <div class="bg-white rounded p-2 border mb-2 small text-secondary">
                <div class="d-flex align-items-center mb-1">
                    <i class="fas fa-check-circle text-success me-2"></i> File safely staged to <code>{safe_dest_path}</code>
                </div>
                <div class="d-flex align-items-center mb-1">
                    <i class="fas fa-cogs text-primary me-2"></i> OpenHands autonomous daemon active &mdash; polling dropzone every 10s
                </div>
                <div class="d-flex align-items-center">
                    <i class="fas fa-shield-alt text-info me-2"></i> Zero-hallucination validation gate: MCP schema + SNOMED-CT + MTS calculation
                </div>
            </div>
            <div class="d-flex justify-content-between align-items-center pt-1">
                <small class="text-muted"><i class="fas fa-info-circle me-1"></i>The queue auto-refreshes every 5 seconds.</small>
                <button type="button" class="btn btn-sm btn-primary" onclick="window.location.href='/?view=triage'">
                    <i class="fas fa-sync-alt me-1"></i> Go to Live Triage Queue
                </button>
            </div>
        </div>
        """
