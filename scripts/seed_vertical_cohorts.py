#!/usr/bin/env python3
"""Seed 15 realistic, HL7 FHIR R4 + GMS OID + SNOMED-CT/LOINC/UCUM specialty bundles."""
import base64
import json
import os

STORE_DIR = "/home/adman-voids/Desktop/Code/slainte-engine/data/fhir_store"
TS = "2026-11-14T09:15:00+00:00"


def _patient(pid, gms, given, family, gender, dob, city, county, phone="+353-21-4901200"):
    return {
        "resource": {
            "resourceType": "Patient",
            "id": pid,
            "identifier": [
                {
                    "use": "official",
                    "system": "urn:oid:2.16.840.1.113883.2.17.1.1",
                    "value": gms,
                }
            ],
            "active": True,
            "name": [{"use": "official", "family": family, "given": given}],
            "telecom": [{"system": "phone", "value": phone, "use": "mobile"}],
            "gender": gender,
            "birthDate": dob,
            "address": [
                {
                    "use": "home",
                    "line": [f"14 {city} Terrace"],
                    "city": city,
                    "district": f"County {county}",
                    "country": "IE",
                }
            ],
        }
    }


def _condition(pid, idx, snomed_code, display_text):
    return {
        "resource": {
            "resourceType": "Condition",
            "id": f"cond-{pid}-{idx}",
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed",
                    }
                ]
            },
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": snomed_code,
                        "display": display_text,
                    }
                ],
                "text": display_text,
            },
            "subject": {"reference": f"Patient/{pid}"},
            "recordedDate": TS,
        }
    }


def _allergy(pid, idx, snomed_code, substance, crit="high", reaction="Anaphylaxis / urticaria"):
    return {
        "resource": {
            "resourceType": "AllergyIntolerance",
            "id": f"alg-{pid}-{idx}",
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                        "display": "Active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                        "display": "Confirmed",
                    }
                ]
            },
            "criticality": crit,
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": snomed_code,
                        "display": substance,
                    }
                ],
                "text": substance,
            },
            "patient": {"reference": f"Patient/{pid}"},
            "recordedDate": TS,
            "reaction": [
                {
                    "manifestation": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "418363000",
                                    "display": reaction,
                                }
                            ],
                            "text": reaction,
                        }
                    ]
                }
            ],
        }
    }


def _med(pid, idx, snomed_code, drug_text, dosage, status="active", note=""):
    res = {
        "resourceType": "MedicationRequest",
        "id": f"med-{pid}-{idx}",
        "status": status,
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": snomed_code,
                    "display": drug_text,
                }
            ],
            "text": drug_text,
        },
        "subject": {"reference": f"Patient/{pid}"},
        "authoredOn": TS,
        "dosageInstruction": [{"text": dosage}],
    }
    if note:
        res["note"] = [{"text": note}]
    return {"resource": res}


def _obs(pid, oid, loinc_code, display, value, unit, ucum_code, category="vital-signs"):
    return {
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-{pid}-{oid}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": category,
                            "display": category.replace("-", " ").title(),
                        }
                    ]
                }
            ],
            "code": {
                "coding": [{"system": "http://loinc.org", "code": loinc_code, "display": display}],
                "text": display,
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": TS,
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": ucum_code,
            },
        }
    }


def _vitals(pid, hr, spo2, sbp, dbp, rr, temp):
    return [
        _obs(pid, "hr", "8867-4", "Heart rate", hr, "beats/minute", "/min"),
        _obs(pid, "spo2", "59408-5", "Oxygen saturation in Arterial blood by Pulse oximetry", spo2, "%", "%"),
        _obs(pid, "sbp", "8480-6", "Systolic blood pressure", sbp, "mmHg", "mm[Hg]"),
        _obs(pid, "dbp", "8462-4", "Diastolic blood pressure", dbp, "mmHg", "mm[Hg]"),
        _obs(pid, "rr", "9279-1", "Respiratory rate", rr, "breaths/minute", "/min"),
        _obs(pid, "temp", "8310-5", "Body temperature", temp, "Cel", "Cel"),
    ]


def _note(pid, idx, title, text, author):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return {
        "resource": {
            "resourceType": "DocumentReference",
            "id": f"doc-{pid}-{idx}",
            "status": "current",
            "type": {
                "coding": [{"system": "http://loinc.org", "code": "11506-3", "display": title}],
                "text": title,
            },
            "subject": {"reference": f"Patient/{pid}"},
            "date": TS,
            "author": [{"display": author}],
            "description": title,
            "content": [
                {
                    "attachment": {
                        "contentType": "text/plain; charset=utf-8",
                        "data": encoded,
                        "title": title,
                        "creation": TS,
                    }
                }
            ],
        }
    }


def _dental_obs(pid, teeth_map, bpe_map, author, notes):
    payload = json.dumps({"teeth": teeth_map, "bpe": bpe_map, "author": author, "notes": notes})
    return {
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-dental-chart-{pid}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "exam",
                            "display": "Exam",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [{"system": "http://loinc.org", "code": "85913-2", "display": "Odontogram chart"}],
                "text": "FDI 32-Tooth Odontogram & BPE Chart",
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": TS,
            "valueString": payload,
        }
    }


def _provenance(pid, prac_id, role_text, sig_text):
    return {
        "resource": {
            "resourceType": "Provenance",
            "id": f"prov-{pid}",
            "target": [{"reference": f"Patient/{pid}"}],
            "recorded": TS,
            "agent": [
                {
                    "role": [{"text": role_text}],
                    "who": {
                        "identifier": {"system": "urn:oid:2.16.840.1.113883.2.1.3.2.4.16.2", "value": prac_id},
                        "display": sig_text,
                    },
                }
            ],
            "signature": [
                {
                    "type": [
                        {
                            "system": "urn:iso-astm:E1762-95:2013",
                            "code": "1.2.840.10065.1.12.1.1",
                            "display": "Author's Signature",
                        }
                    ],
                    "when": TS,
                    "who": {"display": sig_text},
                    "sigFormat": "application/signature+sha256",
                    "data": "c2xhaW50ZS1wcm92ZW5hbmNlLXNpZ25hdHVyZS12MQ==",
                }
            ],
        }
    }


def write_bundle(pid, entries):
    bundle = {
        "resourceType": "Bundle",
        "id": f"bundle-{pid}",
        "type": "collection",
        "timestamp": TS,
        "entry": entries,
    }
    path = os.path.join(STORE_DIR, f"bundle_{pid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
    return path


def main():
    specs = [
        # --- PSYCHIATRY ---
        (
            "PSY101",
            [
                _patient("PSY101", "77101-P", ["Ciaran"], "Kavanagh", "male", "1991-06-14", "Cork", "Cork"),
                _condition("PSY101", 1, "35489007", "Major depressive disorder, recurrent moderate"),
                _condition("PSY101", 2, "21897009", "Generalized anxiety disorder"),
                _allergy("PSY101", 1, "111088007", "Latex", "low", "Contact dermatitis"),
                _med("PSY101", 1, "372594008", "Sertraline 100mg Oral Tablet", "100mg orally every morning"),
                _med("PSY101", 2, "372862008", "Zopiclone 3.75mg Oral Tablet", "3.75mg orally at night PRN (short course)"),
                *_vitals("PSY101", 84, 99, 122, 78, 16, 36.7),
                _obs("PSY101", "phq9", "44261-6", "Patient Health Questionnaire 9 item (PHQ-9) total score", 18, "{score}", "{score}", "survey"),
                _obs("PSY101", "gad7", "70274-6", "Generalized anxiety disorder 7 item (GAD-7) total score", 15, "{score}", "{score}", "survey"),
                _obs("PSY101", "egfr", "33914-3", "Estimated GFR (MDRD)", 92, "mL/min/1.73m2", "mL/min/{1.73_m2}", "laboratory"),
                _obs("PSY101", "k", "2823-3", "Potassium [Moles/volume] in Serum or Plasma", 4.2, "mmol/L", "mmol/L", "laboratory"),
                _note(
                    "PSY101",
                    1,
                    "Psychiatric MSE & Risk Review",
                    "Appearance & Behaviour: Calm, cooperative, good eye contact. Speech: Normal rate and tone. Mood/Affect: Reported 'worn down', affect restricted. Thought Form/Content: No delusional ideation, denies active self-harm or suicidal intent; passive hopelessness discussed. Plan: Continue Sertraline 100mg OD, CBT referral activated, safety plan confirmed.",
                    "Dr. S. Murphy (Consultant Psychiatrist)",
                ),
            ],
        ),
        (
            "PSY102",
            [
                _patient("PSY102", "77102-P", ["Aoife"], "Ni Dhomhnaill", "female", "1978-03-22", "Galway", "Galway"),
                _condition("PSY102", 1, "13746004", "Bipolar affective disorder, stable remission"),
                _condition("PSY102", 2, "700379002", "Chronic kidney disease stage 3B"),
                _allergy("PSY102", 1, "764146007", "Penicillin", "high", "Anaphylaxis"),
                _med("PSY102", 1, "387074009", "Lithium Carbonate 400mg MR Tablet", "400mg orally twice daily", note="Monitor eGFR and trough serum lithium urgently"),
                _med("PSY102", 2, "386850001", "Quetiapine 100mg Oral Tablet", "100mg orally at night"),
                *_vitals("PSY102", 78, 98, 134, 84, 16, 36.8),
                _obs("PSY102", "phq9", "44261-6", "Patient Health Questionnaire 9 item (PHQ-9) total score", 14, "{score}", "{score}", "survey"),
                _obs("PSY102", "gad7", "70274-6", "Generalized anxiety disorder 7 item (GAD-7) total score", 11, "{score}", "{score}", "survey"),
                _obs("PSY102", "egfr", "33914-3", "Estimated GFR (MDRD)", 31, "mL/min/1.73m2", "mL/min/{1.73_m2}", "laboratory"),
                _obs("PSY102", "k", "2823-3", "Potassium [Moles/volume] in Serum or Plasma", 4.6, "mmol/L", "mmol/L", "laboratory"),
                _note(
                    "PSY102",
                    1,
                    "MSE & Lithium Renal Monitoring Note",
                    "Euthymic presentation with mild fatigue. Latest eGFR 31 mL/min triggers renal clearance review for Lithium Carbonate 400mg BD. Repeat trough lithium level ordered today; nephrology co-management letter dispatched.",
                    "Dr. S. Murphy (Consultant Psychiatrist)",
                ),
            ],
        ),
        (
            "PSY103",
            [
                _patient("PSY103", "77103-P", ["Eamonn"], "Gallagher", "male", "1984-11-08", "Dublin", "Dublin"),
                _condition("PSY103", 1, "47505003", "Post-traumatic stress disorder (PTSD)"),
                _condition("PSY103", 2, "82423001", "Chronic neuropathic pain syndrome"),
                _allergy("PSY103", 1, "387406002", "Sulfonamides", "high", "Generalized rash"),
                _med("PSY103", 1, "387264003", "Diazepam 5mg Oral Tablet", "5mg orally PRN anxiety"),
                _med("PSY103", 2, "387494007", "Codeine Phosphate 30mg Oral Tablet", "30mg orally QDS analgesia", note="Review concurrent benzodiazepine CNS depression risk"),
                _med("PSY103", 3, "372490001", "Venlafaxine XL 150mg Capsule", "150mg orally every morning"),
                *_vitals("PSY103", 88, 98, 128, 80, 17, 36.6),
                _obs("PSY103", "phq9", "44261-6", "Patient Health Questionnaire 9 item (PHQ-9) total score", 16, "{score}", "{score}", "survey"),
                _obs("PSY103", "gad7", "70274-6", "Generalized anxiety disorder 7 item (GAD-7) total score", 17, "{score}", "{score}", "survey"),
                _obs("PSY103", "egfr", "33914-3", "Estimated GFR (MDRD)", 78, "mL/min/1.73m2", "mL/min/{1.73_m2}", "laboratory"),
                _note(
                    "PSY103",
                    1,
                    "Trauma Clinic & Medication Safety Review",
                    "Hypervigilance and nocturnal nightmares persisting. Flagged concurrent Diazepam + Codeine combination for respiratory depression taper protocol with GP.",
                    "Dr. L. Byrne (Psychiatry Registrar)",
                ),
            ],
        ),
        # --- DENTISTRY ---
        (
            "DENT101",
            [
                _patient("DENT101", "88101-D", ["Maeve"], "O'Donnell", "female", "1979-08-19", "Limerick", "Limerick"),
                _condition("DENT101", 1, "235096006", "Acute pericoronitis of impacted mandibular third molar (#38)"),
                _condition("DENT101", 2, "49436004", "Atrial fibrillation (Anticoagulated)"),
                _allergy("DENT101", 1, "764146007", "Penicillin", "high", "Severe bronchospasm & urticaria"),
                _med("DENT101", 1, "698090000", "Apixaban 5mg Oral Tablet", "5mg orally twice daily", note="Hold/time surgical extraction around DOAC trough"),
                _med("DENT101", 2, "373444002", "Atorvastatin 20mg Oral Tablet", "20mg orally at night"),
                *_vitals("DENT101", 72, 99, 126, 78, 15, 37.2),
                _dental_obs(
                    "DENT101",
                    {"38": "extraction_planned", "48": "missing", "16": "restored", "26": "endodontic", "46": "crown"},
                    {"ur": "2", "ua": "1", "ul": "2", "lr": "3", "la": "2", "ll": "4"},
                    "Dr. K. Walsh BDS",
                    "Impacted mesioangular #38 with pericoronal swelling. Hemostasis protocol required (Apixaban 5mg BD) and strict Penicillin avoidance.",
                ),
            ],
        ),
        (
            "DENT102",
            [
                _patient("DENT102", "88102-D", ["Tomas"], "Brennan", "male", "1994-04-03", "Cork", "Cork"),
                _condition("DENT102", 1, "328383001", "Symptomatic apical periodontitis tooth #14"),
                _condition("DENT102", 2, "109570007", "Acute dentoalveolar abscess right maxilla"),
                _med("DENT102", 1, "387207008", "Ibuprofen 400mg Oral Tablet", "400mg orally TDS with food"),
                _med("DENT102", 2, "387517004", "Paracetamol 1g Oral Tablet", "1g orally QDS"),
                *_vitals("DENT102", 86, 99, 124, 76, 16, 37.8),
                _dental_obs(
                    "DENT102",
                    {"14": "carious", "15": "endodontic", "36": "restored", "46": "restored"},
                    {"ur": "3", "ua": "1", "ul": "1", "lr": "2", "la": "1", "ll": "1"},
                    "Dr. K. Walsh BDS",
                    "Palatal swelling adjacent #14. Access cavity and I&D performed; RCT Stage 1 dressed with Ca(OH)2.",
                ),
            ],
        ),
        (
            "DENT103",
            [
                _patient("DENT103", "88103-D", ["Niamh"], "Connolly", "female", "1966-12-10", "Waterford", "Waterford"),
                _condition("DENT103", 1, "41565005", "Generalized Stage III periodontitis"),
                _condition("DENT103", 2, "44054006", "Type 2 diabetes mellitus"),
                _allergy("DENT103", 1, "372687004", "Amoxicillin", "high", "Angioedema"),
                _med("DENT103", 1, "372756006", "Warfarin 3mg Oral Tablet", "3mg orally OD per INR clinic", note="Verify INR < 3.5 within 24h prior to subgingival curettage"),
                _med("DENT103", 2, "372567009", "Metformin 500mg Oral Tablet", "500mg orally BD with meals"),
                *_vitals("DENT103", 76, 98, 136, 82, 16, 36.7),
                _dental_obs(
                    "DENT103",
                    {"21": "crown", "16": "missing", "26": "missing", "37": "restored", "47": "carious"},
                    {"ur": "3", "ua": "3", "ul": "3", "lr": "4", "la": "2", "ll": "4"},
                    "Dr. R. Keane BDS",
                    "Post-retained crown fracture margin #21; deep pocketing lower molars.",
                ),
            ],
        ),
        # --- AMBULANCE / EMS ---
        (
            "EMS101",
            [
                _patient("EMS101", "55101-E", ["Cormac"], "Healy", "male", "1962-05-11", "Fermoy", "Cork"),
                _condition("EMS101", 1, "57054005", "Acute anterior ST-Elevation Myocardial Infarction (STEMI)"),
                _condition("EMS101", 2, "38341003", "Essential hypertension"),
                _med("EMS101", 1, "387458008", "Aspirin 300mg Dispersible Tablet", "300mg chewed stat pre-hospital"),
                _med("EMS101", 2, "698805004", "Ticagrelor 180mg Loading Dose", "180mg orally loading per PPCI protocol"),
                *_vitals("EMS101", 118, 91, 88, 54, 26, 36.2),
                _note(
                    "EMS101",
                    1,
                    "NAS Paramedic ePCR Pre-Alert",
                    "12-Lead ECG demonstrates 4mm ST elevation V2-V5. Aspirin 300mg & Ticagrelor 180mg administered on scene. ETA 6 mins direct to Cath Lab Resus Bay 1.",
                    "AP D. Foley (National Ambulance Service)",
                ),
            ],
        ),
        (
            "EMS102",
            [
                _patient("EMS102", "55102-E", ["Roisin"], "Doyle", "female", "1974-09-29", "Clifden", "Galway"),
                _condition("EMS102", 1, "91302008", "Suspected severe urosepsis / Red-Flag Sepsis"),
                _allergy("EMS102", 1, "387406002", "Sulfonamides", "high", "Toxic epidermal necrolysis history"),
                _med("EMS102", 1, "372833007", "Cefuroxime 1.5g IV Infusion", "1.5g IV slow push pre-hospital"),
                *_vitals("EMS102", 126, 93, 92, 58, 25, 39.2),
                _note(
                    "EMS102",
                    1,
                    "HEMS Airway & Sepsis Dispatch ePCR",
                    "RIGORS & hypotension en route N59. Large-bore IV access established, 1000mL Hartmanns + IV Cefuroxime initiated.",
                    "Paramedic M. Connolly (HEMS Medevac)",
                ),
            ],
        ),
        # --- SPORTS MEDICINE ---
        (
            "SPT101",
            [
                _patient("SPT101", "66101-S", ["Cillian"], "Moran", "male", "1999-02-20", "Limerick", "Limerick"),
                _condition("SPT101", 1, "44465007", "Grade 2 biceps femoris hamstring strain (Rehab cleared)"),
                _med("SPT101", 1, "387517004", "Paracetamol 1g Oral Tablet", "1g orally PRN post-session (WADA compliant)"),
                *_vitals("SPT101", 52, 99, 116, 72, 14, 36.6),
                _obs("SPT101", "vo2", "60842-2", "VO2 max aerobic capacity", 64.5, "mL/kg/min", "mL/kg/min", "vital-signs"),
                _provenance("SPT101", "IMC-40912", "Consultant Sports Physician | Match RTP Cleared", "Dr. O. Gallagher FFSEM"),
            ],
        ),
        (
            "SPT102",
            [
                _patient("SPT102", "66102-S", ["Ava"], "Redmond", "female", "2001-07-04", "Athlone", "Westmeath"),
                _condition("SPT102", 1, "110030002", "Sports concussion / mild TBI (SCAT6 Stage 3 Monitor)"),
                _condition("SPT102", 2, "44465007", "Grade 1 medial collateral ligament sprain"),
                _med("SPT102", 1, "373219008", "Diclofenac 1% Topical Gel", "Apply topically BD to right knee"),
                *_vitals("SPT102", 58, 99, 112, 68, 14, 36.8),
                _obs("SPT102", "vo2", "60842-2", "VO2 max aerobic capacity", 58.2, "mL/kg/min", "mL/kg/min", "vital-signs"),
            ],
        ),
        (
            "SPT103",
            [
                _patient("SPT103", "66103-S", ["Shane"], "O'Leary", "male", "1996-10-15", "Killarney", "Kerry"),
                _condition("SPT103", 1, "396275006", "Supraspinatus tendinopathy (Cleared full training)"),
                _med("SPT103", 1, "387517004", "Paracetamol 500mg Oral Tablet", "1g orally PRN"),
                *_vitals("SPT103", 60, 99, 118, 74, 15, 36.7),
                _provenance("SPT103", "IMC-40912", "Lead Squad Physiotherapist & Team MD | RTP Signed", "Dr. O. Gallagher FFSEM"),
            ],
        ),
        # --- ASTRONAUT BIO-TELEMETRY ---
        (
            "AST101",
            [
                _patient("AST101", "99101-A", ["Liam"], "Dempsey", "male", "1983-01-25", "Cologne", "ESA Crew Hub"),
                _condition("AST101", 1, "404684003", "LEO microgravity orthostatic adaptation (Nominal EVA Fit)"),
                _med("AST101", 1, "412279005", "Melatonin 3mg Oral Tablet", "3mg orally prior to orbital sleep cycle"),
                *_vitals("AST101", 64, 98, 114, 70, 14, 36.6),
                _obs("AST101", "egfr", "33914-3", "Estimated GFR (Flight Chemistry)", 96, "mL/min/1.73m2", "mL/min/{1.73_m2}", "laboratory"),
                _obs("AST101", "k", "2823-3", "Serum Potassium", 4.1, "mmol/L", "mmol/L", "laboratory"),
                _provenance("AST101", "ESA-FS-101", "Crew Flight Surgeon | EVA Nominal Cleared", "Col. Dr. H. Richter"),
            ],
        ),
        (
            "AST102",
            [
                _patient("AST102", "99102-A", ["Sorcha"], "Byrne", "female", "1988-06-09", "Cologne", "ESA Crew Hub"),
                _condition("AST102", 1, "404684003", "Spaceflight Associated Neuro-ocular Syndrome (SANS) Surveillance"),
                _med("AST102", 1, "372709008", "Acetazolamide 250mg Oral Tablet", "250mg orally BD per optic disc OCT check"),
                *_vitals("AST102", 76, 96, 128, 82, 16, 36.9),
                _obs("AST102", "k", "2823-3", "Serum Potassium", 3.6, "mmol/L", "mmol/L", "laboratory"),
            ],
        ),
        (
            "AST103",
            [
                _patient("AST103", "99103-A", ["Ronan"], "Hughes", "male", "1981-09-18", "Noordwijk", "ESTEC Sim-Hab"),
                _condition("AST103", 1, "267036007", "Cabin CO2 mild hypercapnia & SpO2 drift monitoring"),
                _med("AST103", 1, "387517004", "Paracetamol 1g Oral Tablet", "1g PRN hypercapnic headache"),
                *_vitals("AST103", 92, 94, 136, 86, 21, 37.1),
                _obs("AST103", "k", "2823-3", "Serum Potassium", 4.4, "mmol/L", "mmol/L", "laboratory"),
            ],
        ),
        (
            "AST104",
            [
                _patient("AST104", "99104-A", ["Elena"], "Kovalenko", "female", "1990-04-12", "Cologne", "ESA Columbus"),
                _condition("AST104", 1, "404684003", "Microgravity bone mineral prophylaxis protocol"),
                _med("AST104", 1, "126223008", "Colecalciferol 2000 IU Capsule", "2000 IU orally once daily"),
                *_vitals("AST104", 59, 99, 112, 68, 13, 36.5),
                _provenance("AST104", "ESA-FS-104", "Flight Surgeon Medical Officer | Nominal Flight Fit", "Col. Dr. H. Richter"),
            ],
        ),
    ]

    for pid, entries in specs:
        p = write_bundle(pid, entries)
        print(f"Wrote {p}")
    print(f"Done seeding {len(specs)} specialty bundles.")


if __name__ == "__main__":
    main()
