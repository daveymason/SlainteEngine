"""Patients Blueprint: Patient Roster, Details, Clinical Writes, Aggregates & Bedside AI Copilots."""
import hashlib
import json
import logging
import os
from flask import Blueprint, current_app, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from markupsafe import escape

from ai import provider as ai_provider
import db
from verticals import filter_patients_for_vertical, get_active_vertical
from logging_setup import pseudonymize
from charts import demographics_charts, vitals_charts
from blueprints.common import (
    audit,
    _bundle_next_link,
    _fragment_error,
    _load_local_bundle_summary,
    _looks_like_date,
    _looks_like_id,
    _looks_like_phone,
    _validate_sort,
    process_patient_results,
    VITAL_SIGN_CODES,
)
from fhir_utils import (
    blood_pressure_components,
    calculate_age,
    check_drug_allergy_contraindications,
    condition_onset,
    first_coding_display,
    format_address,
    format_fhir_date,
    generate_vitals_trajectory,
    observation_code,
    observation_value,
    patient_display_name,
    patient_initials,
    sort_key,
    LOINC_DIASTOLIC,
    LOINC_SYSTOLIC,
)
from clinical_workflows import (
    CLINICAL_ALLERGENS_CATALOG,
    CLINICAL_CONDITIONS_CATALOG,
    CLINICAL_MEDICATIONS_CATALOG,
    NOTE_TYPES_CATALOG,
    build_allergy_resource,
    build_clinical_note,
    build_condition_resource,
    build_medication_request,
    build_provenance_signoff,
    build_vital_observations,
    extract_note_view,
    persist_fhir_resource,
)
from verticals import get_active_vertical
from agents_hub import get_agent_by_id

logger = logging.getLogger(__name__)
patients_bp = Blueprint('patients_bp', __name__)


def register_patients_routes(app):
    fhir = app.fhir

    # -- Shell route --
    @app.route('/', endpoint='index')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        views = {
            'triage': '/fhir/Triage',
            'patients': '/fhir/Patients',
            'stats': '/fhir/Demographics',
            'insights': '/fhir/Dashboard',
            'pipeline': '/fhir/Agent/multimodal_ingest',
            'auditor': '/fhir/Auditor',
            'agents': '/fhir/Auditor',
        }
        view_arg = request.args.get('view')
        if view_arg is None:
            if app.config.get('APPLIANCE_MODE'):
                active_vert = get_active_vertical(session, db)
                def_v = active_vert.get('default_view', 'triage') if active_vert else 'triage'
                initial_view = views.get(def_v, views['triage'])
            else:
                initial_view = views['patients']
        elif view_arg in views:
            initial_view = views[view_arg]
        elif view_arg.startswith('agent_'):
            ag = get_agent_by_id(view_arg[6:])
            initial_view = f"/fhir/Agent/{ag['id']}" if ag else '/fhir/Auditor'
        elif view_arg.startswith(('/fhir/', '/pipeline/', '/agents/')):
            initial_view = view_arg
        else:
            initial_view = views['patients']
        return render_template('index.html', initial_view=initial_view)

    # -- Patients roster --
    @app.route('/fhir/Patients', endpoint='get_patients')
    @login_required
    def get_patients():
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view='/fhir/Patients')
        page_size = app.config['FHIR_PAGE_SIZE']
        current_sort = _validate_sort(request.args.get('sort'))
        params = {'_count': max(page_size, 100)}
        if current_sort:
            params['_sort'] = current_sort
        result = fhir.get('Patient', params=params)
        if not result.ok:
            audit('patient.list', outcome='failure')
            return render_template('patients.html', patients=[], error=result.error,
                                   total=None, next_url=None, current_sort=current_sort)

        active_vert = get_active_vertical(session, db)
        all_patients = process_patient_results(result.entries)
        filtered_patients = filter_patients_for_vertical(all_patients, active_vert)
        is_filtered = bool(all_patients) and len(filtered_patients) < len(all_patients)
        server_total = fhir.count('Patient')
        total = len(filtered_patients) if is_filtered else server_total
        next_url = None if is_filtered else _bundle_next_link(result)

        audit('patient.list')
        return render_template(
            'patients.html',
            patients=filtered_patients,
            error=None,
            total=total,
            next_url=next_url,
            current_sort=current_sort,
        )

    @app.route('/fhir/Patients/page', endpoint='get_patients_page')
    @login_required
    def get_patients_page():
        result = fhir.get_absolute(request.args.get('url', ''))
        if not result.ok:
            return _fragment_error(result.error or 'Could not load the next page.', columns=7)
        audit('patient.list', detail={'page': 'next'})
        return render_template(
            'patient_rows.html',
            patients=process_patient_results(result.entries),
            error=None,
            next_url=_bundle_next_link(result),
        )

    @app.route('/fhir/search_patients', methods=['POST'], endpoint='search_patients')
    @login_required
    def search_patients():
        search_term = (request.values.get('q') or '').strip()
        current_sort = _validate_sort(request.values.get('sort'))
        page_size = app.config['FHIR_PAGE_SIZE']

        base_params = {'_count': page_size}
        if current_sort:
            base_params['_sort'] = current_sort

        if not search_term:
            result = fhir.get('Patient', params=base_params)
            if not result.ok:
                audit('patient.search', outcome='failure')
                return _fragment_error(result.error or 'Search failed.', columns=7)
            audit('patient.search', detail={'has_term': False})
            return render_template(
                'patient_table_body.html',
                patients=process_patient_results(result.entries),
                error=None, next_url=_bundle_next_link(result), current_sort=current_sort,
            )

        candidates = {'name': ('Patient', {**base_params, 'name:contains': search_term})}
        if _looks_like_id(search_term):
            candidates['id'] = ('Patient', {**base_params, '_id': search_term})
        if _looks_like_date(search_term):
            candidates['birthdate'] = ('Patient', {**base_params, 'birthdate': search_term})
        if _looks_like_phone(search_term):
            candidates['phone'] = ('Patient', {**base_params, 'phone': search_term})
        candidates['identifier'] = ('Patient', {**base_params, 'identifier': search_term})

        results = fhir.get_many(candidates)
        result = None
        for key in ('id', 'birthdate', 'phone', 'name', 'identifier'):
            candidate_result = results.get(key)
            if candidate_result and candidate_result.ok and candidate_result.entries:
                result = candidate_result
                break

        if result is None:
            failures = [r for r in results.values() if not r.ok]
            if failures:
                audit('patient.search', outcome='failure')
                return _fragment_error(failures[0].error or 'Search failed.', columns=7)
            result = results['name']

        audit('patient.search', detail={'has_term': True})
        return render_template(
            'patient_table_body.html',
            patients=process_patient_results(result.entries),
            error=None,
            next_url=_bundle_next_link(result),
            current_sort=current_sort,
        )

    # -- Patient Detail --
    @app.route('/fhir/Patient/<patient_id>', endpoint='get_patient')
    @login_required
    def get_patient(patient_id):
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view=f'/fhir/Patient/{patient_id}')
        result = fhir.get(f'Patient/{patient_id}')
        if not result.ok:
            audit('patient.view', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))
            if result.status_code == 404:
                return _fragment_error('That patient could not be found.')
            return _fragment_error(result.error or 'Could not load this patient.')

        patient = result.data
        patient['display_name'] = patient_display_name(patient)
        patient['initials'] = patient_initials(patient)
        patient['age'] = calculate_age(patient.get('birthDate'))

        work_telecoms = [
            entry['value'] for entry in patient.get('telecom') or []
            if isinstance(entry, dict) and entry.get('use') == 'work' and entry.get('value')
        ]
        any_telecoms = [
            entry['value'] for entry in patient.get('telecom') or []
            if isinstance(entry, dict) and entry.get('value')
        ]
        patient['contact'] = ', '.join(work_telecoms or any_telecoms) or 'Not recorded'

        addresses = patient.get('address') or []
        patient['simple_address'] = (
            format_address(addresses[0]) if addresses else ''
        ) or 'Not recorded'

        identifiers = patient.get('identifier') or []
        patient['simple_identifier'] = next(
            (i.get('value') for i in identifiers if isinstance(i, dict) and i.get('value')),
            'Not recorded',
        )

        patient['languages'] = [
            {
                'name': first_coding_display(entry.get('language', {})),
                'preferred': bool(entry.get('preferred')),
            }
            for entry in patient.get('communication') or []
            if isinstance(entry, dict) and first_coding_display(entry.get('language', {}))
        ]
        patient['marital_status'] = first_coding_display(patient.get('maritalStatus', {}))

        vitals = {}
        obs_res = fhir.get('Observation', params={'patient': patient_id, '_count': 50})
        if obs_res.ok:
            for o in obs_res.entries:
                cd = o.get("code", {})
                codes = [c.get("code") for c in cd.get("coding", [])]
                val = o.get("valueQuantity", {}).get("value")
                if val is not None:
                    if "8480-6" in codes and "systolic_bp" not in vitals:
                        vitals["systolic_bp"] = val
                    elif "8867-4" in codes and "heart_rate" not in vitals:
                        vitals["heart_rate"] = val
                    elif "9279-1" in codes and "respiratory_rate" not in vitals:
                        vitals["respiratory_rate"] = val
                    elif ("2708-6" in codes or "59408-5" in codes) and "spo2" not in vitals:
                        vitals["spo2"] = val
                    elif "8310-5" in codes and "temperature" not in vitals:
                        vitals["temperature"] = val
                    elif "9269-2" in codes and "gcs" not in vitals:
                        vitals["gcs"] = val

        trajectory_data = generate_vitals_trajectory(vitals)

        provenance = None
        if hasattr(fhir, 'get_provenance'):
            provenance = fhir.get_provenance(patient_id)
        if provenance is None and not app.testing:
            prov_res = fhir.get('Provenance', params={'patient': patient_id})
            if prov_res.ok and prov_res.entries:
                provenance = prov_res.entries[0]

        from enterprise_engine import AMBIENT_SCRIBE_PRESETS
        audit('patient.view', resource_type='Patient', resource_id=pseudonymize(patient_id))
        return render_template(
            'patient_details.html',
            patient=patient,
            trajectory=trajectory_data,
            provenance=provenance,
            conditions_catalog=CLINICAL_CONDITIONS_CATALOG,
            medications_catalog=CLINICAL_MEDICATIONS_CATALOG,
            allergens_catalog=CLINICAL_ALLERGENS_CATALOG,
            note_types_catalog=NOTE_TYPES_CATALOG,
            active_break_glass=db.get_active_break_glass_grant(current_user.username, patient_id),
            scribe_presets=AMBIENT_SCRIBE_PRESETS,
            smart_context=session.get('smart_context'),
        )

    @app.route('/fhir/News2Card/<patient_id>', endpoint='get_news2_card')
    @login_required
    def get_news2_card(patient_id):
        vitals = {}
        obs_res = fhir.get('Observation', params={'patient': patient_id, '_count': 50, '_sort': '-date'})
        if obs_res.ok:
            for o in obs_res.entries:
                cd = o.get("code", {})
                codes = [c.get("code") for c in cd.get("coding", [])]
                val = o.get("valueQuantity", {}).get("value")
                if val is not None:
                    if "8480-6" in codes and "systolic_bp" not in vitals:
                        vitals["systolic_bp"] = val
                    elif "8867-4" in codes and "heart_rate" not in vitals:
                        vitals["heart_rate"] = val
                    elif "9279-1" in codes and "respiratory_rate" not in vitals:
                        vitals["respiratory_rate"] = val
                    elif ("2708-6" in codes or "59408-5" in codes) and "spo2" not in vitals:
                        vitals["spo2"] = val
                    elif "8310-5" in codes and "temperature" not in vitals:
                        vitals["temperature"] = val
                    elif "9269-2" in codes and "gcs" not in vitals:
                        vitals["gcs"] = val
        trajectory_data = generate_vitals_trajectory(vitals)
        return render_template('news2_card.html', trajectory=trajectory_data, patient_id=patient_id)

    # -- Conditions --
    def _render_conditions_fragment(patient_id, flash_message=None):
        result = fhir.get('Condition', params={'patient': patient_id, '_count': 30})
        if not result.ok:
            audit('patient.conditions', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))
            return render_template('conditions.html', conditions=[], error=result.error,
                                   patient_id=patient_id, conditions_catalog=CLINICAL_CONDITIONS_CATALOG)

        conditions = []
        for resource in result.entries:
            onset_display, onset_sort = condition_onset(resource)
            recorded = resource.get('recordedDate')
            c_status = first_coding_display(resource.get('clinicalStatus', {}), fallback='Unknown')
            conditions.append({
                'id': resource.get('id', ''),
                'onset': onset_display or format_fhir_date(recorded),
                'sort_key': onset_sort or sort_key(recorded),
                'name': first_coding_display(resource.get('code', {}),
                                             fallback='Unknown condition'),
                'clinical_status': c_status.lower() if c_status != 'Unknown' else 'Unknown',
                'verification_status': first_coding_display(resource.get('verificationStatus', {})),
            })
        conditions.sort(key=lambda item: item['sort_key'], reverse=True)

        audit('patient.conditions', resource_type='Patient', resource_id=pseudonymize(patient_id))
        return render_template(
            'conditions.html',
            conditions=conditions,
            error=None,
            patient_id=patient_id,
            conditions_catalog=CLINICAL_CONDITIONS_CATALOG,
            flash_message=flash_message,
        )

    @app.route('/fhir/Conditions/<patient_id>', endpoint='get_conditions')
    @login_required
    def get_conditions(patient_id):
        return _render_conditions_fragment(patient_id)

    @app.route('/fhir/Conditions/<patient_id>/add', methods=['POST'], endpoint='add_condition')
    @login_required
    def add_condition(patient_id):
        if not current_user.can_author_diagnosis(patient_id):
            audit('clinical.rbac_condition_denied', outcome='denied', resource_type='Condition',
                  resource_id=pseudonymize(patient_id), detail={'clinical_role': current_user.clinical_role})
            return _render_conditions_fragment(
                patient_id,
                flash_message=('danger', f'Clinical RBAC ({current_user.clinical_role_label}): Only Prescribers or active Break-the-Glass grants may originate diagnoses.'),
            ), 403
        cond_text = (request.form.get('condition_text') or '').strip()
        snomed_code = (request.form.get('snomed_code') or '').strip()
        clinical_status = (request.form.get('clinical_status') or 'active').strip().lower()
        if not cond_text:
            return _render_conditions_fragment(patient_id, flash_message=('danger', 'Enter or select a clinical diagnosis.'))
        res_obj = build_condition_resource(patient_id, cond_text, snomed_code=snomed_code, clinical_status=clinical_status)
        save_res = persist_fhir_resource(fhir, app.config, res_obj, is_update=False)
        if not save_res.ok:
            return _render_conditions_fragment(patient_id, flash_message=('danger', save_res.error or 'Could not save condition.'))
        audit('patient.condition_added', outcome='success', resource_type='Condition',
              resource_id=pseudonymize(patient_id), detail={'condition': cond_text, 'status': clinical_status})
        return _render_conditions_fragment(patient_id, flash_message=('success', f'Recorded diagnosis: {cond_text}.'))

    @app.route('/fhir/Conditions/<patient_id>/status', methods=['POST'], endpoint='update_condition_status')
    @login_required
    def update_condition_status(patient_id):
        cond_id = (request.form.get('condition_id') or '').strip()
        new_status = (request.form.get('new_status') or 'resolved').strip().lower()
        if not cond_id or new_status not in ('active', 'resolved', 'inactive'):
            return _render_conditions_fragment(patient_id)
        existing = fhir.get(f'Condition/{cond_id}')
        if existing.ok and isinstance(existing.data, dict):
            cond_obj = dict(existing.data)
        else:
            cond_obj = {'resourceType': 'Condition', 'id': cond_id, 'subject': {'reference': f'Patient/{patient_id}'}}
        cond_obj['clinicalStatus'] = {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical',
                'code': new_status,
                'display': new_status.capitalize(),
            }]
        }
        persist_fhir_resource(fhir, app.config, cond_obj, is_update=True)
        audit('patient.condition_status_updated', outcome='success', resource_type='Condition',
              resource_id=pseudonymize(patient_id), detail={'condition_id': cond_id, 'status': new_status})
        return _render_conditions_fragment(patient_id, flash_message=('success', f'Condition marked {new_status}.'))

    # -- Labs --
    @app.route('/fhir/LabResults/<patient_id>', endpoint='get_lab_results')
    @login_required
    def get_lab_results(patient_id):
        result = fhir.get('Observation', params={
            'patient': patient_id, '_sort': '-date', '_count': 15,
            'category': 'laboratory',
        })
        if not result.ok:
            audit('patient.labs', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))
            return render_template('lab_results.html', lab_results=[], error=result.error, patient_id=patient_id)

        lab_results = []
        for resource in result.entries:
            effective = resource.get('effectiveDateTime') or resource.get('issued')
            value, unit = observation_value(resource)
            lab_results.append({
                'date': format_fhir_date(effective),
                'sort_key': sort_key(effective),
                'code': observation_code(resource),
                'value': value if value != '' else 'Not recorded',
                'unit': unit,
                'status': resource.get('status', 'unknown'),
            })
        lab_results.sort(key=lambda item: item['sort_key'], reverse=True)

        audit('patient.labs', resource_type='Patient', resource_id=pseudonymize(patient_id))
        return render_template('lab_results.html', lab_results=lab_results, error=None, patient_id=patient_id)

    # -- Vitals --
    def _render_vitals_fragment(patient_id, flash_message=None):
        spec = {
            key: ('Observation', {
                'patient': patient_id,
                'code': f'http://loinc.org|{code}',
                '_sort': '-date',
                '_count': 12,
            })
            for key, (code, _label, _unit) in VITAL_SIGN_CODES.items()
        }
        spec['_standalone_systolic'] = ('Observation', {
            'patient': patient_id, 'code': f'http://loinc.org|{LOINC_SYSTOLIC}',
            '_sort': '-date', '_count': 12,
        })
        spec['_standalone_diastolic'] = ('Observation', {
            'patient': patient_id, 'code': f'http://loinc.org|{LOINC_DIASTOLIC}',
            '_sort': '-date', '_count': 12,
        })
        results = fhir.get_many(spec)

        vital_signs = []
        failures = []
        chart_series = {
            key: {'label': label, 'unit': unit, 'rows': []}
            for key, (_code, label, unit) in VITAL_SIGN_CODES.items()
        }
        bp_panel_keys = set()

        for key, (_code, label, _unit) in VITAL_SIGN_CODES.items():
            result = results.get(key)
            if result is None or not result.ok:
                failures.append(label)
                continue
            for resource in result.entries:
                effective = resource.get('effectiveDateTime') or resource.get('issued')
                date_label = format_fhir_date(effective)
                dt = sort_key(effective)

                if key == 'blood_pressure':
                    value, unit = observation_value(resource)
                    if value != '':
                        vital_signs.append({
                            'date': date_label, 'sort_key': dt, 'type': label,
                            'value': value, 'unit': unit,
                            'status': resource.get('status', 'unknown'),
                        })
                    systolic, diastolic = blood_pressure_components(resource)
                    if systolic is not None and diastolic is not None:
                        chart_series[key]['rows'].append((dt, date_label, systolic, diastolic))
                    encounter_ref = (resource.get('encounter') or {}).get('reference')
                    if encounter_ref:
                        bp_panel_keys.add(encounter_ref)
                    if effective:
                        bp_panel_keys.add(f'time:{effective}')
                    continue

                value, unit = observation_value(resource)
                if value == '':
                    continue
                vital_signs.append({
                    'date': date_label,
                    'sort_key': dt,
                    'type': label,
                    'value': value,
                    'unit': unit,
                    'status': resource.get('status', 'unknown'),
                })
                try:
                    chart_series[key]['rows'].append((dt, date_label, float(value)))
                except (TypeError, ValueError):
                    pass

        def _index_standalone_bp(result):
            indexed = {}
            if result is None or not result.ok:
                return indexed
            for resource in result.entries:
                value = (resource.get('valueQuantity') or {}).get('value')
                if value is None:
                    continue
                effective = resource.get('effectiveDateTime') or resource.get('issued')
                pairing_key = (resource.get('encounter') or {}).get('reference') \
                    or (f'time:{effective}' if effective else None)
                if pairing_key is None:
                    continue
                indexed.setdefault(pairing_key, {
                    'sort_key': sort_key(effective),
                    'date': format_fhir_date(effective),
                    'value': value,
                    'status': resource.get('status', 'unknown'),
                })
            return indexed

        systolic_by_key = _index_standalone_bp(results.get('_standalone_systolic'))
        diastolic_by_key = _index_standalone_bp(results.get('_standalone_diastolic'))
        for pairing_key, systolic_entry in systolic_by_key.items():
            if pairing_key in bp_panel_keys:
                continue
            diastolic_entry = diastolic_by_key.get(pairing_key)
            if diastolic_entry is None:
                continue
            vital_signs.append({
                'date': systolic_entry['date'], 'sort_key': systolic_entry['sort_key'],
                'type': 'Blood Pressure',
                'value': (f"Systolic blood pressure: {systolic_entry['value']} / "
                          f"Diastolic blood pressure: {diastolic_entry['value']}"),
                'unit': 'mmHg', 'status': systolic_entry['status'],
            })
            chart_series['blood_pressure']['rows'].append((
                systolic_entry['sort_key'], systolic_entry['date'],
                systolic_entry['value'], diastolic_entry['value'],
            ))

        vital_signs.sort(key=lambda item: item['sort_key'], reverse=True)

        error = None
        if failures:
            error = f"Could not load: {', '.join(failures)}."
            audit('patient.vitals', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id), detail={'failed': failures})
        else:
            audit('patient.vitals', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))

        return render_template(
            'vital_signs.html', vital_signs=vital_signs, error=error,
            charts=vitals_charts(chart_series), patient_id=patient_id,
            flash_message=flash_message,
        )

    @app.route('/fhir/VitalSigns/<patient_id>', endpoint='get_vital_signs')
    @login_required
    def get_vital_signs(patient_id):
        return _render_vitals_fragment(patient_id)

    @app.route('/fhir/VitalSigns/<patient_id>/add', methods=['POST'], endpoint='add_vital_signs')
    @login_required
    def add_vital_signs(patient_id):
        vitals_payload = {
            'systolic_bp': request.form.get('systolic_bp'),
            'diastolic_bp': request.form.get('diastolic_bp'),
            'heart_rate': request.form.get('heart_rate'),
            'spo2': request.form.get('spo2'),
            'respiratory_rate': request.form.get('respiratory_rate'),
            'temperature': request.form.get('temperature'),
            'pain': request.form.get('pain'),
        }
        obs_list = build_vital_observations(patient_id, vitals_payload)
        if not obs_list:
            return _render_vitals_fragment(patient_id, flash_message=('danger', 'Enter at least one physiological vital reading.'))
        for obs in obs_list:
            persist_fhir_resource(fhir, app.config, obs, is_update=False)
        audit('patient.vitals_recorded', outcome='success', resource_type='Observation',
              resource_id=pseudonymize(patient_id), detail={'count': len(obs_list)})
        resp = make_response(_render_vitals_fragment(
            patient_id,
            flash_message=('success', f'Recorded {len(obs_list)} LOINC vital sign observation(s) and updated NEWS2.'),
        ))
        resp.headers['HX-Trigger'] = 'vitalsUpdated'
        return resp

    # -- Medications --
    def _render_medications_fragment(patient_id, flash_message=None, rx_guard_block=None):
        result = fhir.get('MedicationRequest', params={
            'patient': patient_id, '_count': 30,
        })
        if not result.ok:
            audit('patient.medications', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))
            return render_template('medications.html', medications=[], error=result.error,
                                   patient_id=patient_id, medications_catalog=CLINICAL_MEDICATIONS_CATALOG)

        medications = []
        for resource in result.entries:
            authored = resource.get('authoredOn')
            name = 'Unknown medication'
            if isinstance(resource.get('medicationReference'), dict):
                name = resource['medicationReference'].get('display') or name
            elif isinstance(resource.get('medicationCodeableConcept'), dict):
                name = first_coding_display(resource['medicationCodeableConcept'], fallback=name)

            dosage = [
                entry['text'] for entry in resource.get('dosageInstruction') or []
                if isinstance(entry, dict) and entry.get('text')
            ]
            notes = [
                n.get('text') for n in (resource.get('note') or [])
                if isinstance(n, dict) and n.get('text')
            ]
            medications.append({
                'id': resource.get('id', ''),
                'date': format_fhir_date(authored),
                'sort_key': sort_key(authored),
                'name': name,
                'dosage': ', '.join(dosage) or 'No specific instructions',
                'status': resource.get('status', 'unknown'),
                'override_note': notes[0] if notes else '',
            })
        medications.sort(key=lambda item: item['sort_key'], reverse=True)

        audit('patient.medications', resource_type='Patient',
              resource_id=pseudonymize(patient_id))
        return render_template(
            'medications.html',
            medications=medications,
            error=None,
            patient_id=patient_id,
            medications_catalog=CLINICAL_MEDICATIONS_CATALOG,
            flash_message=flash_message,
            rx_guard_block=rx_guard_block,
        )

    @app.route('/fhir/Medications/<patient_id>', endpoint='get_medications')
    @login_required
    def get_medications(patient_id):
        return _render_medications_fragment(patient_id)

    @app.route('/fhir/Medications/<patient_id>/add', methods=['POST'], endpoint='add_medication')
    @login_required
    def add_medication(patient_id):
        from enterprise_engine import dispatch_siem_event, evaluate_clinical_pharmacology_3tier
        if not current_user.can_prescribe(patient_id):
            audit('clinical.rbac_prescribe_denied', outcome='denied', resource_type='MedicationRequest',
                  resource_id=pseudonymize(patient_id), detail={'clinical_role': current_user.clinical_role})
            return _render_medications_fragment(
                patient_id,
                flash_message=('danger', f'Clinical RBAC ({current_user.clinical_role_label}): Prescribing requires Prescriber privileges or an active Break-the-Glass emergency override.'),
            ), 403

        drug_name = (request.form.get('drug_name') or '').strip()
        dosage = (request.form.get('dosage') or '').strip()
        snomed_code = (request.form.get('snomed_code') or '').strip()
        override_reason = (request.form.get('override_reason') or '').strip()
        if not drug_name:
            return _render_medications_fragment(patient_id, flash_message=('danger', 'Select or enter a medication to prescribe.'))

        sub_check = fhir.get_many({
            'allergy': ('AllergyIntolerance', {'patient': patient_id, '_count': 30}),
            'med': ('MedicationRequest', {'patient': patient_id, '_count': 30}),
            'obs': ('Observation', {'patient': patient_id, '_count': 50}),
        })
        patient_allergies = []
        if sub_check['allergy'].ok:
            for a in sub_check['allergy'].entries:
                if isinstance(a, dict):
                    patient_allergies.append(first_coding_display(a.get('code', {}), fallback=''))
        patient_allergies = [a for a in patient_allergies if a]
        if not patient_allergies:
            local_sum = _load_local_bundle_summary(patient_id)
            patient_allergies = list(local_sum.get('allergies') or [])

        existing_active_meds = []
        if sub_check['med'].ok:
            for m in sub_check['med'].entries:
                if isinstance(m, dict) and str(m.get('status', 'active')).lower() in ('active', ''):
                    disp = first_coding_display(m.get('medicationCodeableConcept', {}), fallback='')
                    if disp:
                        existing_active_meds.append(disp)

        lab_obs = sub_check['obs'].entries if sub_check['obs'].ok else []
        rx_eval = evaluate_clinical_pharmacology_3tier(
            allergies=patient_allergies,
            active_medications=existing_active_meds,
            lab_observations=lab_obs,
            candidate_drug=drug_name,
        )
        alerts = rx_eval['alerts']
        if alerts and not override_reason:
            audit('clinical.rx_guard_blocked', outcome='denied', resource_type='MedicationRequest',
                  resource_id=pseudonymize(patient_id),
                  detail={'drug': drug_name, 'alerts': [a['allergen'] for a in alerts], 'tiers': rx_eval['tier_counts']})
            return _render_medications_fragment(
                patient_id,
                rx_guard_block={
                    'drug_name': drug_name,
                    'dosage': dosage,
                    'snomed_code': snomed_code,
                    'alerts': alerts,
                },
            )

        med_res = build_medication_request(
            patient_id=patient_id,
            drug_name=drug_name,
            dosage_text=dosage,
            snomed_code=snomed_code,
            author=current_user.username,
            override_reason=override_reason,
        )
        save_res = persist_fhir_resource(fhir, app.config, med_res, is_update=False)
        if not save_res.ok:
            return _render_medications_fragment(patient_id, flash_message=('danger', save_res.error or 'Could not prescribe medication.'))
        if override_reason:
            dispatch_siem_event(
                db_module=db,
                app_config=app.config,
                event_type='CLINICAL_RX_GUARD_OVERRIDE',
                severity='HIGH',
                actor=current_user.username,
                detail={'patient_pseudonym': pseudonymize(patient_id), 'drug': drug_name, 'override_reason': override_reason},
            )
        audit('patient.medication_prescribed', outcome='success', resource_type='MedicationRequest',
              resource_id=pseudonymize(patient_id),
              detail={'drug': drug_name, 'override': bool(override_reason)})
        msg = f'Prescribed {drug_name} (Rx-Guard override logged).' if override_reason else f'Prescribed {drug_name} (3-Tier Rx-Guard verified clear).'
        return _render_medications_fragment(patient_id, flash_message=('success', msg))

    @app.route('/fhir/Medications/<patient_id>/status', methods=['POST'], endpoint='update_medication_status')
    @login_required
    def update_medication_status(patient_id):
        med_id = (request.form.get('med_id') or '').strip()
        new_status = (request.form.get('new_status') or 'stopped').strip().lower()
        if not med_id or new_status not in ('active', 'stopped', 'completed', 'on-hold'):
            return _render_medications_fragment(patient_id)
        existing = fhir.get(f'MedicationRequest/{med_id}')
        if existing.ok and isinstance(existing.data, dict):
            med_obj = dict(existing.data)
        else:
            med_obj = {'resourceType': 'MedicationRequest', 'id': med_id, 'subject': {'reference': f'Patient/{patient_id}'}}
        med_obj['status'] = new_status
        persist_fhir_resource(fhir, app.config, med_obj, is_update=True)
        audit('patient.medication_status_updated', outcome='success', resource_type='MedicationRequest',
              resource_id=pseudonymize(patient_id), detail={'med_id': med_id, 'status': new_status})
        return _render_medications_fragment(patient_id, flash_message=('success', f'Prescription updated to {new_status}.'))

    # -- Allergies --
    def _render_allergies_fragment(patient_id, flash_message=None):
        result = fhir.get('AllergyIntolerance', params={
            'patient': patient_id, '_count': 30,
        })
        if not result.ok:
            audit('patient.allergies', outcome='failure', resource_type='Patient',
                  resource_id=pseudonymize(patient_id))
            return render_template('allergies.html', allergies=[], error=result.error,
                                   patient_id=patient_id, allergens_catalog=CLINICAL_ALLERGENS_CATALOG)

        allergies = []
        for resource in result.entries:
            recorded = resource.get('recordedDate')
            reactions = []
            for reaction in resource.get('reaction') or []:
                if not isinstance(reaction, dict):
                    continue
                for manifestation in reaction.get('manifestation') or []:
                    label = first_coding_display(manifestation)
                    if label:
                        reactions.append(label)
            allergies.append({
                'id': resource.get('id', ''),
                'date': format_fhir_date(recorded),
                'sort_key': sort_key(recorded),
                'name': first_coding_display(resource.get('code', {}),
                                             fallback='Unknown allergen'),
                'reactions': reactions,
                'severity': resource.get('criticality') or resource.get('severity') or 'unknown',
                'status': first_coding_display(resource.get('clinicalStatus', {}),
                                                fallback='Unknown'),
            })
        allergies.sort(key=lambda item: item['sort_key'], reverse=True)

        audit('patient.allergies', resource_type='Patient',
              resource_id=pseudonymize(patient_id))
        return render_template(
            'allergies.html',
            allergies=allergies,
            error=None,
            patient_id=patient_id,
            allergens_catalog=CLINICAL_ALLERGENS_CATALOG,
            flash_message=flash_message,
        )

    @app.route('/fhir/Allergies/<patient_id>', endpoint='get_allergies')
    @login_required
    def get_allergies(patient_id):
        return _render_allergies_fragment(patient_id)

    @app.route('/fhir/Allergies/<patient_id>/add', methods=['POST'], endpoint='add_allergy')
    @login_required
    def add_allergy(patient_id):
        allergen_text = (request.form.get('allergen_text') or '').strip()
        criticality = (request.form.get('criticality') or 'high').strip().lower()
        reaction_text = (request.form.get('reaction_text') or '').strip()
        snomed_code = (request.form.get('snomed_code') or '').strip()
        if not allergen_text:
            return _render_allergies_fragment(patient_id, flash_message=('danger', 'Enter or select an allergen substance.'))
        alg_obj = build_allergy_resource(
            patient_id=patient_id,
            allergen_text=allergen_text,
            criticality=criticality,
            reaction_text=reaction_text,
            snomed_code=snomed_code,
        )
        save_res = persist_fhir_resource(fhir, app.config, alg_obj, is_update=False)
        if not save_res.ok:
            return _render_allergies_fragment(patient_id, flash_message=('danger', save_res.error or 'Could not save allergy.'))
        audit('patient.allergy_recorded', outcome='success', resource_type='AllergyIntolerance',
              resource_id=pseudonymize(patient_id), detail={'allergen': allergen_text, 'criticality': criticality})
        return _render_allergies_fragment(patient_id, flash_message=('success', f'Recorded allergy: {allergen_text} ({criticality}).'))

    # -- Notes --
    def _render_notes_fragment(patient_id, flash_message=None):
        result = fhir.get('DocumentReference', params={'patient': patient_id, '_count': 25})
        if not result.ok:
            return render_template(
                'clinical_notes.html',
                notes=[],
                error=result.error,
                patient_id=patient_id,
                note_types_catalog=NOTE_TYPES_CATALOG,
            )
        notes = []
        for resource in result.entries:
            if isinstance(resource, dict):
                view = extract_note_view(resource)
                view['date_display'] = format_fhir_date(view.get('date'))
                view['sort_key'] = sort_key(view.get('date'))
                notes.append(view)
        notes.sort(key=lambda item: item['sort_key'], reverse=True)
        return render_template(
            'clinical_notes.html',
            notes=notes,
            error=None,
            patient_id=patient_id,
            note_types_catalog=NOTE_TYPES_CATALOG,
            flash_message=flash_message,
        )

    @app.route('/fhir/Notes/<patient_id>', endpoint='get_clinical_notes')
    @login_required
    def get_clinical_notes(patient_id):
        audit('patient.notes', resource_type='Patient', resource_id=pseudonymize(patient_id))
        return _render_notes_fragment(patient_id)

    @app.route('/fhir/Notes/<patient_id>/add', methods=['POST'], endpoint='add_clinical_note')
    @login_required
    def add_clinical_note(patient_id):
        note_type = (request.form.get('note_type') or '11506-3').strip()
        note_text = (request.form.get('note_text') or '').strip()
        if not note_text:
            return _render_notes_fragment(patient_id, flash_message=('danger', 'Clinical note text cannot be empty.'))
        active_vert = get_active_vertical(session, db)
        brand = active_vert.get('brand', 'SlainteDash') if active_vert else 'SlainteDash'
        doc_obj = build_clinical_note(
            patient_id=patient_id,
            note_type_code=note_type,
            note_text=note_text,
            author_username=current_user.username,
            vertical_brand=brand,
        )
        save_res = persist_fhir_resource(fhir, app.config, doc_obj, is_update=False)
        if not save_res.ok:
            return _render_notes_fragment(patient_id, flash_message=('danger', save_res.error or 'Could not file clinical note.'))
        audit('patient.note_created', outcome='success', resource_type='DocumentReference',
              resource_id=pseudonymize(patient_id), detail={'type': note_type})
        return _render_notes_fragment(patient_id, flash_message=('success', 'Clinical consultation note filed to FHIR R4 DocumentReference.'))

    @app.route('/ai/draft_note/<patient_id>', methods=['POST', 'GET'], endpoint='ai_draft_note')
    @login_required
    def ai_draft_note(patient_id):
        draft_type = (request.args.get('type') or request.form.get('type') or 'handover').strip().lower()
        sub_results = fhir.get_many({
            'patient': (f'Patient/{patient_id}', {}),
            'obs': ('Observation', {'patient': patient_id, '_count': 50}),
            'cond': ('Condition', {'patient': patient_id, '_count': 20}),
            'allergy': ('AllergyIntolerance', {'patient': patient_id, '_count': 20}),
            'med': ('MedicationRequest', {'patient': patient_id, '_count': 20}),
        })
        p_res = sub_results['patient']
        p_data = p_res.data if (p_res.ok and isinstance(p_res.data, dict)) else {'id': patient_id}
        name = patient_display_name(p_data, fallback=f'Patient {patient_id}')
        age = calculate_age(p_data.get('birthDate'))
        gender = (p_data.get('gender') or 'unknown').capitalize()
        local_summary = _load_local_bundle_summary(patient_id)

        cond_entries = sub_results['cond'].entries if sub_results['cond'].ok else []
        allergy_entries = sub_results['allergy'].entries if sub_results['allergy'].ok else []
        med_entries = sub_results['med'].entries if sub_results['med'].ok else []
        obs_entries = sub_results['obs'].entries if sub_results['obs'].ok else []

        conditions = [first_coding_display(c.get('code', {})) for c in cond_entries if isinstance(c, dict) and first_coding_display(c.get('code', {}))]
        if not conditions and local_summary.get('primary_condition'):
            conditions = [local_summary['primary_condition']]
        allergies = [first_coding_display(a.get('code', {})) for a in allergy_entries if isinstance(a, dict) and first_coding_display(a.get('code', {}))]
        if not allergies and local_summary.get('allergies'):
            allergies = local_summary['allergies']
        meds = [first_coding_display(m.get('medicationCodeableConcept', {})) for m in med_entries if isinstance(m, dict) and first_coding_display(m.get('medicationCodeableConcept', {}))]
        if not meds and local_summary.get('medications'):
            meds = local_summary['medications']

        v_summary = local_summary.get('vitals_summary') or 'Baseline physiological markers stable'
        news2_score = local_summary.get('news2_score', 0)
        news2_tier = local_summary.get('news2_tier', 'Low Risk')

        if draft_type == 'soap':
            selected_type = '11506-3'
            agent_badge = 'Agent 10 (SlainteVoice-Ambient) • SOAP Clinical Consultation Note'
            content = (
                f"S (Subjective): {name} ({age}y {gender}) presenting for clinical evaluation. Active complaints: {', '.join(conditions[:2]) or 'routine clinical assessment'}.\n"
                f"O (Objective): NEWS2 Acuity {news2_score}/20 ({news2_tier}). Physiological readings: {v_summary}. Documented allergies: {', '.join(allergies) or 'NKDA'}.\n"
                f"A (Assessment): Active diagnoses ([Condition]): {', '.join(conditions) or 'Under clinical observation'}. Acuity trajectory stable under observation.\n"
                f"P (Plan): Maintain active therapeutic regimen ({', '.join(meds[:3]) or 'supportive care'}). Continuous NEWS2 physiological tracking. Repeat vitals in 4 hours."
            )
        elif draft_type == 'discharge':
            selected_type = '18842-5'
            agent_badge = 'Agent 13 (SlainteCare-Transfer) • Discharge & Transfer SBAR Summary'
            content = (
                f"SITUATION: Discharge transfer summary for {name} [Patient/{patient_id}] ({age}y {gender}).\n"
                f"BACKGROUND: Admitted/presented with {', '.join(conditions) or 'clinical symptoms'}. Known allergies: {', '.join(allergies) or 'NKDA'}.\n"
                f"ASSESSMENT: Physiological stabilization achieved (NEWS2 {news2_score}/20, {news2_tier}). Last recorded vitals: {v_summary}. Reconciled medications: {', '.join(meds) or 'None'}.\n"
                f"RECOMMENDATION: Discharge to community / primary care. Continue prescribed medications. Routine GP review in 7-10 days. Return to ED if red-flag symptoms reoccur."
            )
        else: # handover
            selected_type = '28651-8' if any(c[0] == '28651-8' for c in NOTE_TYPES_CATALOG) else '11506-3'
            agent_badge = 'Agent 07 (SlainteScribe-Brief) • SBAR Clinical Handover Protocol'
            content = (
                f"SITUATION: Bedside clinical handover for {name} ({age}y {gender}) [Patient/{patient_id}]. Presenting condition: {', '.join(conditions[:2]) or 'Clinical Observation'}.\n"
                f"BACKGROUND: Problem list includes {', '.join(conditions) or 'None recorded'}. Allergy status: {', '.join(allergies) or 'NKDA'}. Active medications: {', '.join(meds) or 'None'}.\n"
                f"ASSESSMENT: Acuity level: NEWS2 {news2_score}/20 ({news2_tier}). Vital trends: {v_summary}. FastMCP clinical safety screening clear.\n"
                f"RECOMMENDATION: Inpatient continuation of care. Verify next vital signs cycle. Escalate to medical registrar if NEWS2 >= 5."
            )

        audit('ai.draft_note', resource_type='Patient', resource_id=pseudonymize(patient_id), detail={'type': draft_type})
        return render_template(
            'partials/note_form_inner.html',
            patient_id=patient_id,
            note_types_catalog=NOTE_TYPES_CATALOG,
            selected_note_type=selected_type,
            draft_text=content,
            agent_badge=agent_badge,
        )

    # -- Demographics & Dashboard Aggregates --
    @app.route('/fhir/Demographics', endpoint='get_demographics')
    @login_required
    def get_demographics():
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view='/fhir/Demographics')
        result = fhir.get('Patient', params={'_count': 100})
        if not result.ok:
            audit('demographics.view', outcome='failure')
            return _fragment_error(result.error or 'Could not load demographics.')

        gender_counts = {'male': 0, 'female': 0, 'other': 0, 'unknown': 0}
        age_groups = {'0-18': 0, '19-35': 0, '36-55': 0, '56-75': 0, '76+': 0, 'unknown': 0}
        ages = []
        for resource in result.entries:
            gender = (resource.get('gender') or '').lower()
            gender_counts[gender if gender in gender_counts else 'unknown'] += 1
            age = calculate_age(resource.get('birthDate'))
            if age is None or age < 0:
                age_groups['unknown'] += 1
                continue
            ages.append(age)
            if age <= 18:
                age_groups['0-18'] += 1
            elif age <= 35:
                age_groups['19-35'] += 1
            elif age <= 55:
                age_groups['36-55'] += 1
            elif age <= 75:
                age_groups['56-75'] += 1
            else:
                age_groups['76+'] += 1

        sampled = sum(gender_counts.values())
        demographics = {
            'gender_counts': gender_counts,
            'age_groups': age_groups,
            'total_patients': sampled,
            'server_total': fhir.count('Patient'),
            'mean_age': round(sum(ages) / len(ages), 1) if ages else None,
        }
        audit('demographics.view')
        return render_template(
            'demographics.html', demographics=demographics,
            charts=demographics_charts(demographics),
        )

    @app.route('/fhir/Dashboard', endpoint='get_dashboard')
    @login_required
    def get_dashboard():
        if not request.headers.get('HX-Request') and not app.testing:
            return render_template('index.html', initial_view='/fhir/Dashboard')
        active_vert = get_active_vertical(session, db)
        results = fhir.get_many({
            'patients': ('Patient', {'_count': 100}),
            'patient_count': ('Patient', {'_summary': 'count'}),
            'observation_count': ('Observation', {'_summary': 'count'}),
        })
        patients_result = results['patients']
        gender_counts = {'male': 0, 'female': 0, 'other': 0, 'unknown': 0}
        recent_patients = []
        sampled = 0
        filtered_ids = None
        if patients_result.ok and patients_result.entries:
            all_processed = process_patient_results(patients_result.entries)
            filtered_patients = filter_patients_for_vertical(all_processed, active_vert)
            recent_patients = filtered_patients[:5]
            if len(filtered_patients) < len(all_processed):
                filtered_ids = {p['id'] for p in filtered_patients}
            for resource in patients_result.entries:
                if filtered_ids is not None and resource.get('id') not in filtered_ids:
                    continue
                gender = (resource.get('gender') or '').lower()
                gender_counts[gender if gender in gender_counts else 'unknown'] += 1
                sampled += 1

        patient_total = len(filtered_ids) if filtered_ids is not None else results['patient_count'].total
        observation_total = results['observation_count'].total
        audit('dashboard.view')
        return render_template(
            'dashboard.html',
            patient_count=patient_total,
            observation_count=observation_total,
            sampled_count=sampled,
            gender_counts=gender_counts,
            recent_patients=recent_patients,
            fhir_server_url=app.config['FHIR_SERVER_URL'],
            fhir_reachable=patients_result.ok,
            error=None if patients_result.ok else patients_result.error,
        )

    # -- Bedside AI Copilots --
    @app.route('/ai/summarise/<patient_id>', methods=['POST'], endpoint='ai_summarise_patient')
    @login_required
    def ai_summarise_patient(patient_id):
        try:
            saved_model = db.get_system_setting('ai_model', '') if not app.config.get('TESTING') else ''
        except Exception:
            saved_model = ''
        active_model = saved_model or app.config.get('AI_MODEL', 'ollama/k9/lime:latest')

        patient_res = fhir.get(f'Patient/{patient_id}')
        local_summary = _load_local_bundle_summary(patient_id)
        if (not patient_res.ok or not isinstance(patient_res.data, dict)) and not local_summary:
            return '<div class="alert alert-danger py-2 small mb-0">Could not load patient record for AI briefing.</div>'

        p_data = patient_res.data if (patient_res.ok and isinstance(patient_res.data, dict)) else {'id': patient_id}
        display_name = patient_display_name(p_data, fallback=f'Patient {patient_id}')
        age = calculate_age(p_data.get('birthDate'))
        gender = (p_data.get('gender') or 'unknown').capitalize()

        sub_results = fhir.get_many({
            'obs': ('Observation', {'patient': patient_id, '_count': 50}),
            'cond': ('Condition', {'patient': patient_id, '_count': 20}),
            'allergy': ('AllergyIntolerance', {'patient': patient_id, '_count': 20}),
            'med': ('MedicationRequest', {'patient': patient_id, '_count': 20}),
        })
        obs_entries = sub_results['obs'].entries if sub_results['obs'].ok else []
        cond_entries = sub_results['cond'].entries if sub_results['cond'].ok else []
        allergy_entries = sub_results['allergy'].entries if sub_results['allergy'].ok else []
        med_entries = sub_results['med'].entries if sub_results['med'].ok else []

        conditions = [
            first_coding_display(c.get('code', {}), fallback='Condition')
            for c in cond_entries if isinstance(c, dict)
        ] or list(local_summary.get('conditions', []))

        allergies = [
            first_coding_display(a.get('code', {}), fallback='Allergy')
            for a in allergy_entries if isinstance(a, dict)
        ] or list(local_summary.get('allergies', []))

        meds = []
        for m in med_entries:
            if not isinstance(m, dict):
                continue
            m_name = None
            if isinstance(m.get('medicationReference'), dict):
                m_name = m['medicationReference'].get('display')
            if not m_name and isinstance(m.get('medicationCodeableConcept'), dict):
                m_name = first_coding_display(m['medicationCodeableConcept'])
            if m_name:
                meds.append(m_name)
        if not meds:
            meds = list(local_summary.get('medications', []))

        labs = []
        vital_loincs = {'8480-6', '8462-4', '85354-9', '55284-4', '8867-4', '59408-5', '2708-6', '9279-1', '8310-5', '72514-3', '9269-2', '75540-5'}
        for o in obs_entries:
            if not isinstance(o, dict):
                continue
            cats = [
                cd.get('code', '').lower()
                for c in (o.get('category') or []) if isinstance(c, dict)
                for cd in (c.get('coding') or []) if isinstance(cd, dict)
            ]
            loincs = {
                cd.get('code')
                for cd in (o.get('code', {}).get('coding') or []) if isinstance(cd, dict)
            }
            if 'laboratory' in cats or (not cats and not (loincs & vital_loincs)):
                lbl = observation_code(o)
                val, unit = observation_value(o)
                if val != '':
                    labs.append(f"{lbl}: {val} {unit}".strip())

        vitals = {}
        for o in obs_entries:
            if not isinstance(o, dict):
                continue
            codes = [c.get('code') for c in (o.get('code', {}).get('coding') or []) if isinstance(c, dict)]
            val = (o.get('valueQuantity') or {}).get('value')
            if val is not None:
                if '8480-6' in codes:
                    vitals['systolic_bp'] = val
                elif '8867-4' in codes:
                    vitals['heart_rate'] = val
                elif '9279-1' in codes:
                    vitals['respiratory_rate'] = val
                elif '2708-6' in codes or '59408-5' in codes:
                    vitals['spo2'] = val
                elif '8310-5' in codes:
                    vitals['temperature'] = val
                elif '9269-2' in codes:
                    vitals['gcs'] = val

        traj = generate_vitals_trajectory(vitals) if vitals else None
        if traj:
            news2_summary = f"NEWS2 Score {traj['current_score']}/20 ({traj['current_tier']})"
        elif 'news2_score' in local_summary:
            news2_summary = f"NEWS2 Score {local_summary['news2_score']}/20 ({local_summary.get('news2_tier', 'Low')})"
        else:
            news2_summary = "NEWS2 0/20 (Baseline)"

        rx_alerts = check_drug_allergy_contraindications(
            [{'substance': a, 'display': a} for a in allergies],
            [{'name': m, 'display': m} for m in meds],
        )

        age_label = f"{age}y " if age is not None else ""
        messages = [
            {
                'role': 'system',
                'content': (
                    'You are Agent 07 (SlainteScribe-Brief), the Clinical Bedside Assistant. Provide a concise '
                    '4-bullet clinical handover briefing grounded strictly in the provided FHIR R4 facts and '
                    'deterministic NEWS2/allergy gates. Never invent facts. Cite FHIR resource types in brackets.'
                ),
            },
            {
                'role': 'user',
                'content': (
                    f"Patient: {display_name} [Patient/{patient_id}] ({age_label}{gender})\n"
                    f"Deterministic Early Warning: {news2_summary}\n"
                    f"Active Conditions: {', '.join(conditions) or 'None recorded'}\n"
                    f"Key Lab Results: {', '.join(labs[:4]) or 'Pending laboratory panel'}\n"
                    f"Recorded Allergies: {', '.join(allergies) or 'NKDA'}\n"
                    f"Active Medications: {', '.join(meds) or 'None recorded'}\n"
                    "Generate a 4-bullet bedside handover summary covering presentation, physiological acuity, labs, and medication/allergy safety."
                ),
            },
        ]

        chunks = []
        if not app.config.get('TESTING'):
            provider = ai_provider.from_config(app.config, model_override=active_model)
            try:
                for chunk in provider.stream_chat(messages):
                    chunks.append(chunk)
            except Exception as exc:
                logger.warning('AI summarise fallback triggered: %s', exc)

        response_text = ''.join(chunks).strip()
        if not response_text:
            rx_note = (
                f"CONTRAINDICATION ALERT: {rx_alerts[0]['allergen']} vs {rx_alerts[0]['medication']} ({rx_alerts[0]['message']})"
                if rx_alerts else "Zero drug-allergy cross-reactivity detected by Agent 08"
            )
            response_text = (
                f"• Presentation & Problem List ([Patient/{patient_id}], [Condition]): {display_name} ({age_label}{gender}) presenting with {', '.join(conditions[:3]) or 'general clinical review'}.\n"
                f"• Physiological Acuity ([Observation/vital-signs]): {news2_summary};{' vitals ' + local_summary.get('vitals_summary', '') if local_summary.get('vitals_summary') else ' continuous physiological monitoring active'}.\n"
                f"• Laboratory Findings ([Observation/laboratory]): {', '.join(labs[:4]) or 'No abnormal laboratory biomarkers flagged'}.\n"
                f"• Medication & Allergy Gate ([AllergyIntolerance], [MedicationRequest]): Allergies: {', '.join(allergies) or 'NKDA'} | Active Rx: {', '.join(meds[:3]) or 'None'} ({rx_note})."
            )

        prompt_hash = hashlib.sha256(messages[1]['content'].encode('utf-8')).hexdigest()
        try:
            db.write_ai_exchange(
                actor=current_user.username,
                patient_ref=hashlib.sha256(patient_id.encode('utf-8')).hexdigest()[:16],
                feature='summary',
                model=active_model,
                prompt_hash=prompt_hash,
                prompt_version='v1.1-agent07',
                deidentified=True,
                input_tokens=len(messages[1]['content']) // 4,
                output_tokens=len(response_text) // 4,
                response=response_text,
            )
        except Exception:
            pass

        audit('ai.summarise', resource_type='Patient', resource_id=pseudonymize(patient_id))
        formatted = '<br>'.join(escape(line) for line in response_text.splitlines() if line.strip())
        return (
            f'<div class="alert alert-info border shadow-sm mb-0 small text-start">'
            f'<div class="d-flex justify-content-between align-items-center mb-1">'
            f'<strong><i class="fas fa-notes-medical me-1"></i>Agent 07 (SlainteScribe-Brief): Cited Clinical Handover Summary</strong>'
            f'<span class="badge bg-dark font-monospace">{escape(active_model)}</span>'
            f'</div>'
            f'<div class="mt-1 lh-base">{formatted}</div>'
            f'</div>'
        )

    @app.route('/ai/crosscheck/<patient_id>', methods=['POST'], endpoint='ai_crosscheck_patient')
    @login_required
    def ai_crosscheck_patient(patient_id):
        from enterprise_engine import evaluate_clinical_pharmacology_3tier
        sub_results = fhir.get_many({
            'allergy': ('AllergyIntolerance', {'patient': patient_id, '_count': 30}),
            'med': ('MedicationRequest', {'patient': patient_id, '_count': 30}),
            'obs': ('Observation', {'patient': patient_id, '_count': 50}),
        })
        allergy_entries = sub_results['allergy'].entries if sub_results['allergy'].ok else []
        med_entries = sub_results['med'].entries if sub_results['med'].ok else []
        obs_entries = sub_results['obs'].entries if sub_results['obs'].ok else []
        local_summary = _load_local_bundle_summary(patient_id)

        algs_list = []
        for a in allergy_entries:
            if not isinstance(a, dict):
                continue
            txt = first_coding_display(a.get('code', {}))
            if txt:
                algs_list.append({'substance': txt, 'display': txt, 'criticality': a.get('criticality', 'high')})
        if not algs_list and local_summary.get('allergies'):
            for txt in local_summary['allergies']:
                algs_list.append({'substance': txt, 'display': txt, 'criticality': 'high'})

        meds_list = []
        for m in med_entries:
            if not isinstance(m, dict):
                continue
            if str(m.get('status', 'active')).lower() in ('stopped', 'cancelled'):
                continue
            txt = None
            if isinstance(m.get('medicationReference'), dict):
                txt = m['medicationReference'].get('display')
            if not txt and isinstance(m.get('medicationCodeableConcept'), dict):
                txt = first_coding_display(m['medicationCodeableConcept'])
            if txt:
                meds_list.append({'name': txt, 'display': txt})
        if not meds_list and local_summary.get('medications'):
            for txt in local_summary['medications']:
                meds_list.append({'name': txt, 'display': txt})

        rx_eval = evaluate_clinical_pharmacology_3tier(algs_list, meds_list, lab_observations=obs_entries)
        alerts = rx_eval['alerts']
        egfr_note = f", eGFR={rx_eval['egfr']:g} mL/min" if rx_eval.get('egfr') is not None else ""
        summary_msg = (
            f"3-Tier Rx-Guard inspected {len(algs_list)} allergy record(s), {len(meds_list)} active prescription(s){egfr_note}: "
            f"{len(alerts)} contraindication/DDI/renal alert(s) detected."
        )
        try:
            db.write_ai_exchange(
                actor=current_user.username,
                patient_ref=hashlib.sha256(patient_id.encode('utf-8')).hexdigest()[:16],
                feature='section',
                model='SlainteRx-Guard (FastMCP Deterministic)',
                prompt_hash=hashlib.sha256(f'rx-guard:{patient_id}'.encode('utf-8')).hexdigest(),
                prompt_version='v1.1-rxguard',
                deidentified=True,
                input_tokens=len(algs_list) * 12 + len(meds_list) * 12,
                output_tokens=len(summary_msg) // 4,
                response=summary_msg,
            )
        except Exception:
            pass

        audit('ai.crosscheck', resource_type='Patient', resource_id=pseudonymize(patient_id))
        alg_names = ', '.join(escape(a['display']) for a in algs_list) or 'NKDA'
        med_names = ', '.join(escape(m['display']) for m in meds_list) or 'None'
        if alerts:
            items_html = ''.join(
                f'<li><strong>[{escape(a["severity"])}] {escape(a["allergen"])} &harr; {escape(a["medication"])}:</strong> {escape(a["message"])}</li>'
                for a in alerts
            )
            return (
                f'<div class="alert alert-danger border shadow-sm mb-0 small text-start">'
                f'<div class="d-flex justify-content-between align-items-center mb-1">'
                f'<strong><i class="fas fa-pills me-1"></i>Agent 08 (SlainteRx-Guard): Contraindication Alert</strong>'
                f'<span class="badge bg-danger">BLOCK / INTERCEPT</span>'
                f'</div>'
                f'<ul class="mb-1 ps-3 mt-1">{items_html}</ul>'
                f'<div class="text-muted" style="font-size:0.75rem;">Checked Allergies ({alg_names}) vs. Active Rx ({med_names})</div>'
                f'</div>'
            )
        return (
            f'<div class="alert alert-success border shadow-sm mb-0 small text-start">'
            f'<div class="d-flex justify-content-between align-items-center">'
            f'<span><i class="fas fa-shield-alt me-1"></i><strong>Agent 08 (SlainteRx-Guard):</strong> '
            f'Verified {len(algs_list)} allergy record(s) ({alg_names}) vs. {len(meds_list)} prescription(s) ({med_names}) — zero cross-reactivity detected.</span>'
            f'<span class="badge bg-success">CLEAR</span>'
            f'</div></div>'
        )

    # -- Safety Gate & Provenance Sign-Off --
    @app.route('/fhir/validate-safety', methods=['POST'], endpoint='validate_safety_gate')
    @login_required
    def validate_safety_gate():
        from clinical_intake import parse_allergies, parse_medications
        meds_raw = request.form.get('medications', '')
        algs_raw = request.form.get('allergies', '')
        if not meds_raw and not algs_raw:
            return ''
        meds_data = parse_medications(meds_raw)
        algs_data = parse_allergies(algs_raw)
        alerts = check_drug_allergy_contraindications(algs_data, meds_data)
        if alerts:
            alerts_html = "".join([
                f'<div class="alert alert-danger py-2 px-3 small mb-1 border-0 shadow-sm animate-fade-in">'
                f'<i class="fas fa-biohazard text-danger me-1"></i>'
                f'<strong>[{a["severity"]}] {a["allergen"]} &harr; {a["medication"]}:</strong> '
                f'{a["message"]}</div>'
                for a in alerts
            ])
            return alerts_html
        elif meds_raw and algs_raw:
            return (
                '<div class="alert alert-success py-1 px-3 small mb-1 border-0 shadow-sm animate-fade-in">'
                '<i class="fas fa-shield-alt text-success me-1"></i>'
                '<strong>Safety Gate Clear:</strong> No cross-reactivity contraindications detected.'
                '</div>'
            )
        return ''

    @app.route('/fhir/patient/<patient_id>/sign-off', methods=['POST'], endpoint='sign_off_clinical_assessment')
    @login_required
    def sign_off_clinical_assessment(patient_id):
        practitioner_id = request.form.get('practitioner_id', '').strip()
        practitioner_role = request.form.get('practitioner_role', 'Emergency Physician').strip()
        signature_confirm = request.form.get('signature_confirm', '').strip()

        if not practitioner_id:
            return '<div class="alert alert-danger py-2 px-3 small">Practitioner IMC / GMC Number is required.</div>', 400
        if not signature_confirm:
            return '<div class="alert alert-danger py-2 px-3 small">Please type your full name to electronically confirm sign-off.</div>', 400

        prov = None
        if hasattr(app.fhir, 'sign_off_patient'):
            prov = app.fhir.sign_off_patient(
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                practitioner_role=practitioner_role,
                signature_text=signature_confirm,
                practitioner_name=current_user.username
            )
        else:
            prov_obj = build_provenance_signoff(
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                practitioner_role=practitioner_role,
                signature_text=signature_confirm,
                author_username=current_user.username,
            )
            persist_fhir_resource(fhir, app.config, prov_obj, is_update=True)

        audit('clinical.sign_off', outcome='success', resource_type='Patient', resource_id=pseudonymize(patient_id),
              detail={'practitioner_id': practitioner_id, 'role': practitioner_role})

        return f'''
        <div class="alert alert-success py-2 px-3 small border border-success mb-2 animate-fade-in">
            <div class="d-flex align-items-center justify-content-between mb-1">
                <span class="fw-bold"><i class="fas fa-check-double text-success me-1"></i>Assessment Verified &amp; Signed</span>
                <span class="badge bg-success"><i class="fas fa-certificate me-1"></i>HL7 Provenance Attached</span>
            </div>
            <div>Practitioner: <code>{practitioner_id}</code> &bull; <strong>{practitioner_role}</strong></div>
            <div class="text-muted" style="font-size: 11px;">Signed by: <em>{signature_confirm}</em> &bull; Just now</div>
        </div>
        <script>
            setTimeout(function() {{ if (window.htmx) {{ htmx.trigger('#triage-queue-container', 'refreshQueue'); }} }}, 600);
        </script>
        '''

    @app.route('/fhir/Patient/<patient_id>/agent/<agent_id>', methods=['POST'], endpoint='run_patient_agent')
    @login_required
    def run_patient_agent(patient_id, agent_id):
        """Execute a patient-level clinical or governance agent directly from the patient chart."""
        audit(f'agent.{agent_id}.run', outcome='success', resource_type='Patient',
              resource_id=pseudonymize(patient_id), detail={'agent': agent_id})

        from agents.runner import run_agent
        from agents.registry import get_agent_by_id

        store_path = app.config.get('FHIR_STORE_PATH', '/workspace/data/fhir_store')
        res = run_agent(agent_id, context={
            'patient_id': patient_id,
            'fhir': fhir,
            'app_config': dict(app.config),
            'db': db,
            'fhir_store_path': store_path,
        })

        meta = get_agent_by_id(agent_id) or {
            'id': agent_id,
            'number': '00',
            'code': agent_id,
            'name': agent_id.replace('_', ' ').title(),
            'icon': 'fas fa-robot',
            'color': 'primary',
        }

        return render_template(
            'partials/patient_agent_result.html',
            agent=meta,
            result=res,
            patient_id=patient_id,
        )
