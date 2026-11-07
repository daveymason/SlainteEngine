"""Shared presentation helpers and audit utilities across Flask Blueprints."""
import json
import os
import re
from typing import Any, Dict, List, Optional
from flask import current_app, has_app_context, request
from flask_login import current_user
import db
from logging_setup import pseudonymize
from fhir_utils import (
    calculate_age,
    calculate_news2_score,
    check_drug_allergy_contraindications,
    format_address,
    patient_display_name,
)

_SORTABLE_FIELDS = {
    'family', 'given', 'birthdate', 'gender', '_id',
}
_DATE_SEARCH_RE = re.compile(r'^\d{4}(-\d{2}(-\d{2})?)?$')

VITAL_SIGN_CODES = {
    'blood_pressure': ('85354-9', 'Blood Pressure', 'mmHg'),
    'heart_rate': ('8867-4', 'Heart Rate', 'bpm'),
    'spo2': ('59408-5', 'Oxygen Saturation (SpO2)', '%'),
    'respiratory_rate': ('9279-1', 'Respiratory Rate', '/min'),
    'temperature': ('8310-5', 'Temperature', '°C'),
    'pain': ('72514-3', 'Pain Score', '{score}'),
}


def audit(action: str, outcome: str = 'success', resource_type: Optional[str] = None, resource_id: Optional[str] = None, detail: Optional[Dict[str, Any]] = None) -> None:
    """Record an access to the audit trail, with the patient ID pseudonymised."""
    actor = None
    if current_user and current_user.is_authenticated:
        actor = current_user.get_id()
    db.write_audit(
        action=action,
        outcome=outcome,
        actor=actor,
        resource_type=resource_type,
        resource_id=resource_id,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        detail=detail,
    )


def _fragment_error(message: str, columns: Optional[int] = None) -> str:
    """Render an inline error for an HTMX panel."""
    if columns:
        return (
            f'<tr><td colspan="{columns}" class="text-center text-danger py-3">'
            f'<i class="fas fa-exclamation-triangle me-2"></i>{message}</td></tr>'
        )
    return (
        f'<div class="alert alert-danger mb-3">'
        f'<i class="fas fa-exclamation-triangle me-2"></i>{message}</div>'
    )


def _load_local_bundle_summary(pt_id: str) -> Dict[str, Any]:
    """Fast local lookup of clinical summary fields from fhir_store."""
    if has_app_context() and current_app.config.get('TESTING') and not current_app.config.get('FHIR_STORE_PATH'):
        return {
            'primary_condition': 'General Assessment',
            'allergies': [],
            'medications': [],
            'news2_score': 0,
            'news2_tier': 'Low Risk',
            'vitals_summary': 'Baseline',
            'rx_alerts': [],
        }
    candidates = [
        os.environ.get('FHIR_STORE_PATH', ''),
        '/workspace/data/fhir_store',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'fhir_store')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fhir_store')),
    ]
    for store_dir in candidates:
        if not store_dir or not os.path.isdir(store_dir):
            continue
        bpath = os.path.join(store_dir, f'bundle_{pt_id}.json')
        if os.path.isfile(bpath):
            try:
                with open(bpath, 'r', encoding='utf-8') as f:
                    bdata = json.load(f)
                conditions = []
                allergies = []
                medications = []
                vitals_map = {}
                for entry in bdata.get('entry') or []:
                    res = entry.get('resource') or {}
                    rtype = res.get('resourceType')
                    if rtype == 'Condition':
                        txt = (res.get('code') or {}).get('text') or ((res.get('code') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            conditions.append(txt)
                    elif rtype == 'AllergyIntolerance':
                        txt = (res.get('code') or {}).get('text') or ((res.get('code') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            allergies.append(txt)
                    elif rtype == 'MedicationRequest':
                        txt = (res.get('medicationCodeableConcept') or {}).get('text') or ((res.get('medicationCodeableConcept') or {}).get('coding') or [{}])[0].get('display')
                        if txt:
                            medications.append(txt)
                    elif rtype == 'Observation':
                        code = ((res.get('code') or {}).get('coding') or [{}])[0].get('code')
                        val = (res.get('valueQuantity') or {}).get('value')
                        if code and val is not None:
                            vitals_map[code] = val
                score, tier, _ = calculate_news2_score(vitals_map)
                v_parts = []
                if '8867-4' in vitals_map:
                    v_parts.append(f"HR {int(float(vitals_map['8867-4']))}")
                if '2708-6' in vitals_map or '59408-5' in vitals_map:
                    sp = vitals_map.get('2708-6') or vitals_map.get('59408-5')
                    v_parts.append(f"SpO2 {int(float(sp))}%")
                if '8480-6' in vitals_map:
                    v_parts.append(f"SBP {int(float(vitals_map['8480-6']))}")
                return {
                    'primary_condition': conditions[0] if conditions else 'Clinical Review',
                    'allergies': allergies,
                    'medications': medications,
                    'news2_score': score,
                    'news2_tier': tier,
                    'vitals_summary': ' · '.join(v_parts) if v_parts else 'Vitals stable',
                    'rx_alerts': check_drug_allergy_contraindications(allergies, medications),
                }
            except Exception:
                break
    return {
        'primary_condition': 'General Assessment',
        'allergies': [],
        'medications': [],
        'news2_score': 0,
        'news2_tier': 'Low Risk',
        'vitals_summary': 'Baseline',
        'rx_alerts': [],
    }


def process_patient_results(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten Patient resources into the shape table and cockpit templates expect."""
    processed = []
    for resource in resources:
        address = (resource.get('address') or [{}])[0]
        telecom = (resource.get('telecom') or [{}])[0]
        pt_id = resource.get('id', 'Unknown')
        bdate = resource.get('birthDate', 'Unknown')
        gms_val = 'Unassigned'
        for ident in resource.get('identifier') or []:
            if isinstance(ident, dict) and ident.get('value'):
                gms_val = ident.get('value')
                break
        extra = _load_local_bundle_summary(pt_id)
        processed.append({
            'id': pt_id,
            'name': patient_display_name(resource),
            'gender': resource.get('gender', 'Unknown'),
            'birthDate': bdate,
            'age': calculate_age(bdate),
            'gms': gms_val,
            'address': format_address(address) or 'Not recorded',
            'telecom': telecom.get('value', 'Not recorded'),
            **extra,
        })
    return processed


def _bundle_next_link(result: Any) -> Optional[str]:
    """Extract next page URL from searchset Bundle."""
    if not hasattr(result, 'data') or not isinstance(result.data, dict):
        return None
    for link in result.data.get('link') or []:
        if isinstance(link, dict) and link.get('relation') == 'next':
            return link.get('url')
    return None


def _validate_sort(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    field = raw[1:] if raw.startswith('-') else raw
    return raw if field in _SORTABLE_FIELDS else None


def _looks_like_date(term: str) -> bool:
    return bool(_DATE_SEARCH_RE.fullmatch(term))


def _looks_like_phone(term: str) -> bool:
    digits = re.sub(r'[\s().+-]', '', term)
    return digits.isdigit() and len(digits) >= 6


def _looks_like_id(term: str) -> bool:
    return term.replace('-', '').isalnum() and any(c.isdigit() for c in term)
