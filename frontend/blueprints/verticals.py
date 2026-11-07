"""Verticals Blueprint: 8-Vertical Specialty Cockpit Workspaces and Clinical Actions."""
import json as _json
import os
import time as _time
import uuid as _uuid
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

import db
from logging_setup import pseudonymize
from blueprints.common import audit, process_patient_results
from verticals import VERTICALS_CATALOG, get_active_vertical, get_vertical_list
from fhir_utils import (
    first_coding_display,
    format_fhir_date,
    observation_code,
    observation_value,
    sort_key,
    check_drug_allergy_contraindications,
    calculate_news2_score,
)
from clinical_workflows import (
    ALL_FDI_TEETH,
    BPE_SEXTANTS,
    CLINICAL_CONDITIONS_CATALOG,
    CLINICAL_MEDICATIONS_CATALOG,
    FDI_LOWER_LEFT,
    FDI_LOWER_RIGHT,
    FDI_UPPER_LEFT,
    FDI_UPPER_RIGHT,
    TOOTH_STATUS_META,
    build_clinical_note,
    build_dental_chart_observation,
    build_provenance_signoff,
    build_vital_observations,
    extract_note_view,
    now_iso,
    parse_dental_chart_observation,
    persist_fhir_resource,
)

verticals_bp = Blueprint('verticals_bp', __name__)


def _render_cockpit_workspace(app, patient_id_override=None, flash_message=None, epcr_result=None):
    fhir = app.fhir
    active_vert = get_active_vertical(session, db)
    v_key = (request.args.get('vertical') or (active_vert['key'] if active_vert else 'ed')).strip().lower()
    if v_key not in VERTICALS_CATALOG:
        v_key = 'ed'
    vert_meta = VERTICALS_CATALOG[v_key]

    pt_res = fhir.get('Patient', params={'_count': 40})
    cohort_patients = process_patient_results(pt_res.entries) if pt_res.ok else []
    patients_by_id = {p['id']: p for p in cohort_patients}

    ctx = {
        'v_key': v_key,
        'vert_meta': vert_meta,
        'cohort_patients': cohort_patients,
        'flash_message': flash_message,
        'epcr_result': epcr_result,
        'medications_catalog': CLINICAL_MEDICATIONS_CATALOG,
        'conditions_catalog': CLINICAL_CONDITIONS_CATALOG,
    }

    if v_key == 'dentist':
        default_pid = 'patient-case-8' if 'patient-case-8' in patients_by_id else (cohort_patients[0]['id'] if cohort_patients else 'patient-case-8')
        selected_pid = (patient_id_override or request.args.get('patient_id') or default_pid).strip()
        sub = fhir.get_many({
            'obs': ('Observation', {'patient': selected_pid, '_count': 30}),
            'alg': ('AllergyIntolerance', {'patient': selected_pid, '_count': 20}),
            'med': ('MedicationRequest', {'patient': selected_pid, '_count': 20}),
            'cond': ('Condition', {'patient': selected_pid, '_count': 20}),
        })
        obs_entries = sub['obs'].entries if sub['obs'].ok else []
        alg_entries = sub['alg'].entries if sub['alg'].ok else []
        med_entries = sub['med'].entries if sub['med'].ok else []
        cond_entries = sub['cond'].entries if sub['cond'].ok else []

        dental_chart = parse_dental_chart_observation(obs_entries, selected_pid)
        allergies_list = [first_coding_display(a.get('code', {}), fallback='') for a in alg_entries if isinstance(a, dict)]
        allergies_list = [a for a in allergies_list if a]
        meds_list = []
        for m in med_entries:
            if isinstance(m, dict) and m.get('status') in (None, 'active'):
                m_txt = first_coding_display(m.get('medicationCodeableConcept', {}), fallback='')
                if m_txt:
                    meds_list.append(m_txt)
        conditions_list = [first_coding_display(c.get('code', {}), fallback='') for c in cond_entries if isinstance(c, dict)]
        conditions_list = [c for c in conditions_list if c]

        anticoag_keywords = ('warfarin', 'apixaban', 'rivaroxaban', 'ticagrelor', 'clopidogrel', 'aspirin', 'dabigatran')
        hemostasis_flags = [m for m in meds_list if any(k in m.lower() for k in anticoag_keywords)]
        penicillin_flag = any('penicillin' in a.lower() or 'amoxicillin' in a.lower() for a in allergies_list)

        ctx.update({
            'selected_pid': selected_pid,
            'selected_patient': patients_by_id.get(selected_pid, {'id': selected_pid, 'name': selected_pid, 'identifier': 'N/A'}),
            'dental_chart': dental_chart,
            'teeth_json': _json.dumps(dental_chart['teeth']),
            'fdi_upper_right': FDI_UPPER_RIGHT,
            'fdi_upper_left': FDI_UPPER_LEFT,
            'fdi_lower_right': FDI_LOWER_RIGHT,
            'fdi_lower_left': FDI_LOWER_LEFT,
            'tooth_status_meta': TOOTH_STATUS_META,
            'bpe_sextants': BPE_SEXTANTS,
            'allergies_list': allergies_list,
            'meds_list': meds_list,
            'conditions_list': conditions_list,
            'hemostasis_flags': hemostasis_flags,
            'penicillin_flag': penicillin_flag,
        })

    elif v_key == 'pharmacy':
        med_res = fhir.get('MedicationRequest', params={'_count': 60})
        alg_res = fhir.get('AllergyIntolerance', params={'_count': 80})
        allergies_by_pt = {}
        if alg_res.ok:
            for a in alg_res.entries:
                if not isinstance(a, dict):
                    continue
                p_ref = ((a.get('patient') or a.get('subject') or {}).get('reference') or '').replace('Patient/', '')
                a_name = first_coding_display(a.get('code', {}), fallback='')
                if p_ref and a_name:
                    allergies_by_pt.setdefault(p_ref, []).append(a_name)

        dispense_queue = []
        if med_res.ok:
            for m in med_res.entries:
                if not isinstance(m, dict):
                    continue
                p_ref = ((m.get('subject') or {}).get('reference') or '').replace('Patient/', '')
                pt_info = patients_by_id.get(p_ref, {})
                pt_name = pt_info.get('name') or p_ref or 'Patient'
                gms = pt_info.get('identifier') or 'Unverified'
                drug_name = 'Unknown medication'
                if isinstance(m.get('medicationReference'), dict):
                    drug_name = m['medicationReference'].get('display') or drug_name
                elif isinstance(m.get('medicationCodeableConcept'), dict):
                    drug_name = first_coding_display(m['medicationCodeableConcept'], fallback=drug_name)
                dosage_list = [d.get('text') for d in (m.get('dosageInstruction') or []) if isinstance(d, dict) and d.get('text')]
                pt_algs = allergies_by_pt.get(p_ref) or pt_info.get('allergies') or []
                rx_alerts = check_drug_allergy_contraindications(pt_algs, [drug_name])
                notes = [n.get('text') for n in (m.get('note') or []) if isinstance(n, dict) and n.get('text')]
                status_val = (m.get('status') or 'active').lower()
                dispense_queue.append({
                    'id': m.get('id', ''),
                    'patient_id': p_ref,
                    'patient_name': pt_name,
                    'gms': gms,
                    'drug_name': drug_name,
                    'dosage': ', '.join(dosage_list) or 'Standard regimen',
                    'status': status_val,
                    'date': format_fhir_date(m.get('authoredOn')),
                    'sort_key': sort_key(m.get('authoredOn')),
                    'allergies': pt_algs,
                    'rx_alerts': rx_alerts,
                    'note': notes[-1] if notes else '',
                })
        dispense_queue.sort(key=lambda item: (0 if item['status'] == 'active' else 1, 0 if item['rx_alerts'] else 1))
        ctx.update({
            'dispense_queue': dispense_queue[:35],
            'pending_count': sum(1 for x in dispense_queue if x['status'] == 'active'),
            'flagged_count': sum(1 for x in dispense_queue if x['status'] == 'active' and x['rx_alerts']),
            'dispensed_count': sum(1 for x in dispense_queue if x['status'] == 'completed'),
            'hold_count': sum(1 for x in dispense_queue if x['status'] in ('on-hold', 'stopped')),
        })

    elif v_key == 'gp':
        default_pid = 'patient-case-6' if 'patient-case-6' in patients_by_id else (cohort_patients[0]['id'] if cohort_patients else 'patient-case-6')
        selected_pid = (patient_id_override or request.args.get('patient_id') or default_pid).strip()
        sub = fhir.get_many({
            'labs': ('Observation', {'patient': selected_pid, 'category': 'laboratory', '_count': 12}),
            'med': ('MedicationRequest', {'patient': selected_pid, '_count': 20}),
            'cond': ('Condition', {'patient': selected_pid, '_count': 20}),
            'notes': ('DocumentReference', {'patient': selected_pid, '_count': 10}),
        })
        labs_list = []
        if sub['labs'].ok:
            for o in sub['labs'].entries:
                if isinstance(o, dict):
                    val, unit = observation_value(o)
                    if val != '':
                        labs_list.append({'label': observation_code(o), 'value': f"{val} {unit}".strip(), 'date': format_fhir_date(o.get('effectiveDateTime'))})
        meds_list = []
        if sub['med'].ok:
            for m in sub['med'].entries:
                if isinstance(m, dict):
                    d_name = first_coding_display(m.get('medicationCodeableConcept', {}), fallback='Medication')
                    d_inst = ', '.join([d.get('text') for d in (m.get('dosageInstruction') or []) if isinstance(d, dict) and d.get('text')])
                    meds_list.append({
                        'id': m.get('id', ''),
                        'name': d_name,
                        'dosage': d_inst or 'Repeat 28-day supply',
                        'status': m.get('status', 'active'),
                        'date': format_fhir_date(m.get('authoredOn')),
                    })
        conds_list = []
        if sub['cond'].ok:
            for c in sub['cond'].entries:
                if isinstance(c, dict):
                    conds_list.append(first_coding_display(c.get('code', {}), fallback='Condition'))
        notes_list = []
        if sub['notes'].ok:
            for doc in sub['notes'].entries:
                if isinstance(doc, dict):
                    nv = extract_note_view(doc)
                    nv['date_display'] = format_fhir_date(nv.get('date'))
                    notes_list.append(nv)

        ctx.update({
            'selected_pid': selected_pid,
            'selected_patient': patients_by_id.get(selected_pid, {'id': selected_pid, 'name': selected_pid, 'identifier': 'N/A', 'vitals_summary': 'Stable'}),
            'cdm_labs': labs_list,
            'cdm_meds': meds_list,
            'cdm_conditions': conds_list,
            'gp_notes': notes_list[:5],
        })

    elif v_key == 'psychiatry':
        from enterprise_engine import evaluate_clinical_pharmacology_3tier
        default_pid = 'patient-case-4' if 'patient-case-4' in patients_by_id else (cohort_patients[0]['id'] if cohort_patients else 'patient-case-4')
        selected_pid = (patient_id_override or request.args.get('patient_id') or default_pid).strip()
        sub = fhir.get_many({
            'obs': ('Observation', {'patient': selected_pid, '_count': 30}),
            'med': ('MedicationRequest', {'patient': selected_pid, '_count': 20}),
            'cond': ('Condition', {'patient': selected_pid, '_count': 20}),
            'alg': ('AllergyIntolerance', {'patient': selected_pid, '_count': 20}),
            'notes': ('DocumentReference', {'patient': selected_pid, '_count': 10}),
        })
        obs_entries = sub['obs'].entries if sub['obs'].ok else []
        med_entries = sub['med'].entries if sub['med'].ok else []
        alg_entries = sub['alg'].entries if sub['alg'].ok else []
        phq9_latest = None
        gad7_latest = None
        for o in obs_entries:
            if not isinstance(o, dict):
                continue
            codes = [c.get('code') for c in (o.get('code', {}).get('coding') or []) if isinstance(c, dict)]
            val, _u = observation_value(o)
            if '44261-6' in codes and phq9_latest is None and val != '':
                phq9_latest = val
            if '70274-6' in codes and gad7_latest is None and val != '':
                gad7_latest = val

        meds_for_eval = []
        psych_meds = []
        for m in med_entries:
            if isinstance(m, dict):
                d_name = first_coding_display(m.get('medicationCodeableConcept', {}), fallback='Medication')
                d_inst = ', '.join([d.get('text') for d in (m.get('dosageInstruction') or []) if isinstance(d, dict) and d.get('text')])
                st = m.get('status', 'active')
                psych_meds.append({'id': m.get('id', ''), 'name': d_name, 'dosage': d_inst or 'Daily oral regimen', 'status': st})
                if str(st).lower() not in ('stopped', 'cancelled'):
                    meds_for_eval.append({'name': d_name, 'display': d_name})
        algs_for_eval = [
            {'substance': first_coding_display(a.get('code', {})), 'display': first_coding_display(a.get('code', {}))}
            for a in alg_entries if isinstance(a, dict) and first_coding_display(a.get('code', {}))
        ]
        rx_eval = evaluate_clinical_pharmacology_3tier(algs_for_eval, meds_for_eval, lab_observations=obs_entries)
        psych_notes = []
        if sub['notes'].ok:
            for doc in sub['notes'].entries:
                if isinstance(doc, dict):
                    nv = extract_note_view(doc)
                    nv['date_display'] = format_fhir_date(nv.get('date'))
                    psych_notes.append(nv)

        ctx.update({
            'selected_pid': selected_pid,
            'selected_patient': patients_by_id.get(selected_pid, {'id': selected_pid, 'name': selected_pid, 'identifier': 'N/A', 'vitals_summary': 'Stable'}),
            'psych_meds': psych_meds,
            'psych_conditions': [first_coding_display(c.get('code', {}), fallback='Condition') for c in (sub['cond'].entries if sub['cond'].ok else []) if isinstance(c, dict)],
            'psych_rx_eval': rx_eval,
            'phq9_latest': phq9_latest,
            'gad7_latest': gad7_latest,
            'psych_notes': psych_notes[:5],
        })

    elif v_key in ('ems', 'ed'):
        acute_arrivals = sorted(
            cohort_patients,
            key=lambda p: (p.get('news2_score', 0), 1 if p['id'].startswith('P') else 0),
            reverse=True,
        )[:6]
        ctx.update({
            'acute_arrivals': acute_arrivals,
        })

    elif v_key in ('sports', 'astro'):
        prov_res = fhir.get('Provenance', params={'_count': 60})
        signed_by_pt = {}
        if prov_res.ok:
            for pr in prov_res.entries:
                if not isinstance(pr, dict):
                    continue
                for tgt in (pr.get('target') or []):
                    t_ref = (tgt.get('reference') or '').replace('Patient/', '')
                    if t_ref:
                        signed_by_pt[t_ref] = pr
        preferred_ids = ['patient-case-7', 'P104', 'P105', 'P102', 'P103', 'P106', 'patient-case-4', 'patient-case-1']
        ordered = []
        seen = set()
        for pid in preferred_ids:
            if pid in patients_by_id:
                ordered.append(patients_by_id[pid])
                seen.add(pid)
        for p in cohort_patients:
            if p['id'] not in seen and len(ordered) < 8:
                ordered.append(p)
                seen.add(p['id'])

        roster_board = []
        for p in ordered:
            pid = p['id']
            prov = signed_by_pt.get(pid)
            if not prov and hasattr(fhir, 'get_provenance'):
                prov = fhir.get_provenance(pid)
            roster_board.append({
                **p,
                'cleared': prov is not None,
                'clearance_role': (((prov or {}).get('agent') or [{}])[0].get('role') or [{}])[0].get('text', '') if prov else '',
                'clearance_time': format_fhir_date((prov or {}).get('recorded')) if prov else '',
            })
        ctx.update({
            'roster_board': roster_board,
            'cleared_count': sum(1 for r in roster_board if r['cleared']),
            'pending_clearance_count': sum(1 for r in roster_board if not r['cleared']),
        })

    return render_template('cockpit_workspace.html', **ctx)


def register_verticals_routes(app):
    fhir = app.fhir

    @app.route('/verticals/switch', methods=['POST'], endpoint='switch_vertical')
    @login_required
    def switch_vertical():
        v_key = (request.form.get('vertical_key') or 'ed').strip().lower()
        if v_key not in VERTICALS_CATALOG:
            v_key = 'ed'
        session['active_vertical'] = v_key
        db.set_system_setting('default_vertical', v_key)
        vert = VERTICALS_CATALOG[v_key]
        audit('vertical.switched', outcome='success', detail={'vertical': v_key, 'brand': vert['brand']})
        target_view = vert.get('default_view', 'triage')
        return redirect(url_for('index', view=target_view))

    @app.route('/fhir/VerticalWorkspace', endpoint='get_vertical_workspace')
    @app.route('/fhir/CockpitWorkspace', endpoint='get_cockpit_workspace')
    @login_required
    def get_cockpit_workspace():
        return _render_cockpit_workspace(app)

    @app.route('/fhir/Vertical/dentist/save', methods=['POST'])
    @app.route('/fhir/Cockpit/dentist/save', methods=['POST'], endpoint='save_dentist_chart')
    @login_required
    def save_dentist_chart():
        patient_id = (request.form.get('patient_id') or 'patient-case-8').strip()
        raw_teeth = request.form.get('teeth_json') or '{}'
        dental_notes = (request.form.get('dental_notes') or '').strip()
        try:
            teeth_map = _json.loads(raw_teeth)
            if not isinstance(teeth_map, dict):
                teeth_map = {}
        except Exception:
            teeth_map = {}
        clean_teeth = {
            t: (teeth_map.get(t) if teeth_map.get(t) in TOOTH_STATUS_META else 'sound')
            for t in ALL_FDI_TEETH
        }
        bpe_map = {
            sex_key: (request.form.get(f'bpe_{sex_key}') or '0').strip()
            for sex_key, _lbl in BPE_SEXTANTS
        }
        obs_obj = build_dental_chart_observation(
            patient_id=patient_id,
            teeth_map=clean_teeth,
            bpe_map=bpe_map,
            author_username=current_user.username,
            notes=dental_notes,
        )
        persist_fhir_resource(fhir, app.config, obs_obj, is_update=True)
        if dental_notes:
            note_obj = build_clinical_note(
                patient_id=patient_id,
                note_type_code='28570-0',
                note_text=f"FDI Odontogram & BPE Update (BPE {bpe_map['ur']}/{bpe_map['ua']}/{bpe_map['ul']} | {bpe_map['lr']}/{bpe_map['la']}/{bpe_map['ll']}): {dental_notes}",
                author_username=current_user.username,
                vertical_brand='SlainteDent',
            )
            persist_fhir_resource(fhir, app.config, note_obj, is_update=False)
        audit('cockpit.dental_chart_saved', outcome='success', resource_type='Observation',
              resource_id=pseudonymize(patient_id), detail={'bpe': bpe_map})
        return _render_cockpit_workspace(
            app,
            patient_id_override=patient_id,
            flash_message=('success', f'Saved 32-tooth FDI Odontogram & 6-sextant BPE chart for {patient_id} to FHIR R4.'),
        )

    @app.route('/fhir/Vertical/pharmacy/dispense', methods=['POST'])
    @app.route('/fhir/Cockpit/pharmacy/dispense', methods=['POST'], endpoint='pharmacy_dispense_action')
    @login_required
    def pharmacy_dispense_action():
        if not current_user.can_dispense():
            audit('cockpit.pharmacy_rbac_denied', outcome='denied', resource_type='MedicationRequest',
                  detail={'clinical_role': current_user.clinical_role})
            return _render_cockpit_workspace(
                app,
                flash_message=('danger', f'Clinical RBAC ({current_user.clinical_role_label}): Only Supervising Pharmacists or Admins may verify & dispense prescriptions.'),
            ), 403
        med_id = (request.form.get('med_id') or '').strip()
        patient_id = (request.form.get('patient_id') or '').strip()
        new_status = (request.form.get('new_status') or 'completed').strip().lower()
        pharm_note = (request.form.get('pharm_note') or '').strip()
        if not med_id or new_status not in ('completed', 'on-hold', 'stopped', 'active'):
            return _render_cockpit_workspace(app, flash_message=('danger', 'Invalid prescription dispense parameters.'))

        existing = fhir.get(f'MedicationRequest/{med_id}')
        if existing.ok and isinstance(existing.data, dict):
            med_obj = dict(existing.data)
        else:
            med_obj = {'resourceType': 'MedicationRequest', 'id': med_id, 'subject': {'reference': f'Patient/{patient_id}'}}
        med_obj['status'] = new_status
        action_label = {
            'completed': 'Dispensed & PSI Verified',
            'on-hold': 'Placed On-Hold (Prescriber Query)',
            'stopped': 'Cancelled / Stopped',
            'active': 'Returned to Active Queue',
        }[new_status]
        notes_arr = list(med_obj.get('note') or [])
        notes_arr.append({
            'text': f"{action_label} by {current_user.username}" + (f": {pharm_note}" if pharm_note else ""),
            'time': now_iso(),
        })
        med_obj['note'] = notes_arr
        persist_fhir_resource(fhir, app.config, med_obj, is_update=True)
        audit('cockpit.pharmacy_dispense', outcome='success', resource_type='MedicationRequest',
              resource_id=pseudonymize(patient_id or med_id), detail={'med_id': med_id, 'status': new_status})
        return _render_cockpit_workspace(
            app,
            flash_message=('success', f'Prescription {med_id}: {action_label}.'),
        )

    @app.route('/fhir/Vertical/gp/soap', methods=['POST'])
    @app.route('/fhir/Cockpit/gp/soap', methods=['POST'], endpoint='gp_file_soap_note')
    @login_required
    def gp_file_soap_note():
        patient_id = (request.form.get('patient_id') or 'patient-case-6').strip()
        subj = (request.form.get('soap_s') or '').strip()
        obj = (request.form.get('soap_o') or '').strip()
        assess = (request.form.get('soap_a') or '').strip()
        plan = (request.form.get('soap_p') or '').strip()
        sbp = (request.form.get('gp_sbp') or '').strip()
        dbp = (request.form.get('gp_dbp') or '').strip()
        hr = (request.form.get('gp_hr') or '').strip()

        if not any([subj, obj, assess, plan]):
            return _render_cockpit_workspace(
                app,
                patient_id_override=patient_id,
                flash_message=('danger', 'Complete at least one SOAP consultation section before filing.'),
            )

        composed = (
            f"SUBJECTIVE: {subj or 'Reviewed in clinic.'}\n"
            f"OBJECTIVE: {obj or 'Stable examination.'}"
            + (f" Clinic BP {sbp}/{dbp} mmHg, HR {hr} bpm." if sbp and dbp else "")
            + f"\nASSESSMENT: {assess or 'Chronic disease review'}\n"
            f"PLAN: {plan or 'Continue current management & safety-netting.'}"
        )
        doc_obj = build_clinical_note(
            patient_id=patient_id,
            note_type_code='11506-3',
            note_text=composed,
            author_username=current_user.username,
            vertical_brand='SlainteGP',
        )
        persist_fhir_resource(fhir, app.config, doc_obj, is_update=False)

        if any([sbp, dbp, hr]):
            for v_obs in build_vital_observations(patient_id, {'systolic_bp': sbp, 'diastolic_bp': dbp, 'heart_rate': hr}):
                persist_fhir_resource(fhir, app.config, v_obs, is_update=False)

        audit('cockpit.gp_soap_filed', outcome='success', resource_type='DocumentReference',
              resource_id=pseudonymize(patient_id))
        return _render_cockpit_workspace(
            app,
            patient_id_override=patient_id,
            flash_message=('success', f'SOAP consultation & CDM review filed for {patient_id}.'),
        )

    @app.route('/fhir/Vertical/gp/renew', methods=['POST'])
    @app.route('/fhir/Cockpit/gp/renew', methods=['POST'], endpoint='gp_renew_repeat_rx')
    @login_required
    def gp_renew_repeat_rx():
        patient_id = (request.form.get('patient_id') or 'patient-case-6').strip()
        med_id = (request.form.get('med_id') or '').strip()
        existing = fhir.get(f'MedicationRequest/{med_id}') if med_id else None
        if existing and existing.ok and isinstance(existing.data, dict):
            med_obj = dict(existing.data)
            med_obj['status'] = 'active'
            med_obj['authoredOn'] = now_iso()
            notes_arr = list(med_obj.get('note') or [])
            notes_arr.append({'text': f'28-day repeat prescription renewed by GP {current_user.username}', 'time': now_iso()})
            med_obj['note'] = notes_arr
            persist_fhir_resource(fhir, app.config, med_obj, is_update=True)
            drug_label = first_coding_display(med_obj.get('medicationCodeableConcept', {}), fallback=med_id)
            audit('cockpit.gp_repeat_renewed', outcome='success', resource_type='MedicationRequest',
                  resource_id=pseudonymize(patient_id), detail={'med_id': med_id})
            return _render_cockpit_workspace(
                app,
                patient_id_override=patient_id,
                flash_message=('success', f'Renewed 28-day repeat prescription: {drug_label}.'),
            )
        return _render_cockpit_workspace(
            app,
            patient_id_override=patient_id,
            flash_message=('danger', 'Could not locate repeat prescription to renew.'),
        )

    @app.route('/fhir/Vertical/ems/epcr', methods=['POST'])
    @app.route('/fhir/Cockpit/ems/epcr', methods=['POST'], endpoint='ems_transmit_epcr')
    @login_required
    def ems_transmit_epcr():
        from clinical_intake import (
            MTS_METADATA, build_fhir_bundle, calculate_mts_category,
            parse_allergies, parse_medications, resolve_snomed,
        )
        full_name = (request.form.get('full_name') or '').strip() or 'Unidentified Pre-Hospital Casualty'
        dob = (request.form.get('dob') or '1975-04-12').strip()
        gender = (request.form.get('gender') or 'unknown').strip().lower()
        gms_number = (request.form.get('gms_number') or '').strip()
        complaint = (request.form.get('complaint') or '').strip() or 'Acute pre-hospital emergency ambulance transfer'

        def _fval(k):
            v = (request.form.get(k) or '').strip()
            try:
                return float(v) if v else None
            except ValueError:
                return None

        vitals = {
            'systolic_bp': _fval('systolic_bp'),
            'diastolic_bp': _fval('diastolic_bp'),
            'heart_rate': _fval('heart_rate'),
            'spo2': _fval('spo2'),
            'respiratory_rate': _fval('respiratory_rate'),
            'temperature': _fval('temperature'),
            'pain': _fval('pain'),
            'complaint': complaint,
        }
        mts_cat = calculate_mts_category(vitals)
        mts_info = MTS_METADATA.get(mts_cat, MTS_METADATA[2])
        news2_score, news2_tier, _ = calculate_news2_score(vitals)
        snomed_code, _ = resolve_snomed(complaint)

        pt_id = f"P{int(_time.time() * 1000) % 9000 + 1000}"
        if not gms_number:
            gms_number = f"EMS-{pt_id}-IE"

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
            medications=meds_data,
            allergies=algs_data,
        )
        if hasattr(fhir, 'save_bundle'):
            fhir.save_bundle(bundle, f"bundle_{pt_id}.json")
        else:
            fhir.post('Bundle', json_data=bundle)
            if not app.config.get('TESTING'):
                store_dir = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
                if not os.path.isdir(store_dir):
                    store_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'fhir_store'))
                if os.path.isdir(store_dir):
                    with open(os.path.join(store_dir, f"bundle_{pt_id}.json"), 'w', encoding='utf-8') as bf:
                        _json.dump(bundle, bf, indent=2)

        audit('cockpit.ems_epcr_transmitted', outcome='success', resource_type='Bundle',
              resource_id=pseudonymize(pt_id), detail={'mts_cat': mts_cat, 'news2': news2_score})

        epcr_summary = {
            'patient_id': pt_id,
            'full_name': full_name,
            'gms_number': gms_number,
            'complaint': complaint,
            'snomed_code': snomed_code,
            'mts_cat': mts_cat,
            'mts_name': mts_info['name'],
            'mts_target': mts_info['target_time_minutes'],
            'news2_score': news2_score,
            'news2_tier': news2_tier,
        }
        return _render_cockpit_workspace(
            app,
            epcr_result=epcr_summary,
            flash_message=('success', f'ePCR Pre-Alert transmitted to Receiving ED: {full_name} ({pt_id}) — MTS Cat {mts_cat} / NEWS2 {news2_score}.'),
        )

    @app.route('/fhir/Vertical/clearance/<patient_id>', methods=['POST'])
    @app.route('/fhir/Cockpit/clearance/<patient_id>', methods=['POST'], endpoint='sign_cockpit_clearance')
    @login_required
    def sign_cockpit_clearance(patient_id):
        active_vert = get_active_vertical(session, db)
        v_key = active_vert['key'] if active_vert else 'sports'
        default_role = 'Flight Surgeon — EVA Medical Clearance' if v_key == 'astro' else 'Sports Medicine Physician — SCAT6 Return-to-Play'
        clearance_role = (request.form.get('clearance_role') or default_role).strip()
        reg_id = (request.form.get('practitioner_id') or f'IMC-{current_user.username.upper()}-01').strip()
        clearance_note = (request.form.get('clearance_note') or 'Cleared following deterministic bio-telemetry & neurological review.').strip()

        prov_obj = build_provenance_signoff(
            patient_id=patient_id,
            practitioner_id=reg_id,
            practitioner_role=clearance_role,
            signature_text=current_user.username,
            author_username=current_user.username,
        )
        if hasattr(fhir, 'sign_off_patient'):
            fhir.sign_off_patient(
                patient_id=patient_id,
                practitioner_id=reg_id,
                practitioner_role=clearance_role,
                signature_text=current_user.username,
                practitioner_name=current_user.username,
            )
        persist_fhir_resource(fhir, app.config, prov_obj, is_update=True)

        doc_obj = build_clinical_note(
            patient_id=patient_id,
            note_type_code='34109-9',
            note_text=f"{clearance_role} ({reg_id}): {clearance_note}",
            author_username=current_user.username,
            vertical_brand=active_vert.get('brand', 'SlainteSport') if active_vert else 'SlainteSport',
        )
        persist_fhir_resource(fhir, app.config, doc_obj, is_update=False)

        audit('cockpit.medical_clearance_signed', outcome='success', resource_type='Provenance',
              resource_id=pseudonymize(patient_id), detail={'role': clearance_role, 'reg_id': reg_id})
        return _render_cockpit_workspace(
            app,
            flash_message=('success', f'Signed cryptographic FHIR Provenance ({clearance_role}) for {patient_id}.'),
        )

    @app.route('/fhir/Vertical/psychiatry/assess', methods=['POST'])
    @app.route('/fhir/Cockpit/psychiatry/assess', methods=['POST'], endpoint='psychiatry_file_mse_assessment')
    @login_required
    def psychiatry_file_mse_assessment():
        patient_id = (request.form.get('patient_id') or 'patient-case-4').strip()
        phq9_raw = (request.form.get('phq9_score') or '').strip()
        gad7_raw = (request.form.get('gad7_score') or '').strip()
        risk_tier = (request.form.get('risk_tier') or 'Low Acute Risk — Community CMHT Follow-Up').strip()
        mse_text = (request.form.get('mse_notes') or '').strip()

        if not mse_text and not phq9_raw and not gad7_raw:
            return _render_cockpit_workspace(
                app,
                patient_id_override=patient_id,
                flash_message=('danger', 'Provide at least a PHQ-9/GAD-7 score or Mental State Examination summary.'),
            )

        recorded_scales = []
        for loinc_code, loinc_display, raw_val in [
            ('44261-6', 'Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]', phq9_raw),
            ('70274-6', 'Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]', gad7_raw),
        ]:
            if raw_val != '':
                try:
                    num_val = int(float(raw_val))
                    scale_obs = {
                        'resourceType': 'Observation',
                        'id': f"obs-psych-{_uuid.uuid4().hex[:10]}",
                        'status': 'final',
                        'category': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/observation-category', 'code': 'survey', 'display': 'Survey'}]}],
                        'code': {'coding': [{'system': 'http://loinc.org', 'code': loinc_code, 'display': loinc_display}], 'text': loinc_display},
                        'subject': {'reference': f'Patient/{patient_id}'},
                        'effectiveDateTime': now_iso(),
                        'valueQuantity': {'value': num_val, 'unit': '{score}', 'system': 'http://unitsofmeasure.org', 'code': '{score}'},
                    }
                    persist_fhir_resource(fhir, app.config, scale_obs, is_update=False)
                    recorded_scales.append(f"{'PHQ-9' if loinc_code == '44261-6' else 'GAD-7'}={num_val}")
                except ValueError:
                    pass

        composed_mse = (
            f"PSYCHIATRY MSE & RISK STRATIFICATION ({risk_tier})\n"
            + (f"Rating Scales: {', '.join(recorded_scales)}\n" if recorded_scales else "")
            + f"Mental State & Plan: {mse_text or 'Routine psychiatric review completed; safety plan reinforced.'}"
        )
        doc_obj = build_clinical_note(
            patient_id=patient_id,
            note_type_code='11488-4',
            note_text=composed_mse,
            author_username=current_user.username,
            vertical_brand='SlaintePsych',
        )
        persist_fhir_resource(fhir, app.config, doc_obj, is_update=False)
        audit('vertical.psychiatry_mse_filed', outcome='success', resource_type='DocumentReference',
              resource_id=pseudonymize(patient_id), detail={'scales': recorded_scales, 'risk_tier': risk_tier})
        return _render_cockpit_workspace(
            app,
            patient_id_override=patient_id,
            flash_message=('success', f'Mental State Examination & LOINC rating scales ({", ".join(recorded_scales) or "MSE Note"}) persisted to FHIR R4 for {patient_id}.'),
        )
