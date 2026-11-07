import React from 'react';
import type { AgentRecord } from '@/data/agentsData';
import type { VerticalLayoutVariant } from '@/data/verticalsData';

/**
 * Bespoke factual architecture schematic per Health-Tech Agent.
 * Same clean SVG frame across all 11 agent pages, customized with each agent's exact pipeline & badges.
 */
export function AgentSchematicSvg({ agent }: { agent: AgentRecord }) {
  const accent =
    agent.squadColor === 'error'
      ? '#EF4444'
      : agent.squadColor === 'warning'
      ? '#F59E0B'
      : '#38BDF8';

  return (
    <svg
      viewBox="0 0 480 300"
      width="100%"
      height="auto"
      role="img"
      aria-label={`${agent.name} (${agent.codeName}) deterministic FastMCP architecture diagram`}
      style={{ display: 'block', borderRadius: 12 }}
    >
      <rect width="480" height="300" rx="12" fill="#0F172A" stroke="#334155" strokeWidth="2" />
      {/* Top terminal bar */}
      <rect x="1" y="1" width="478" height="38" rx="11" fill="#1E293B" />
      <circle cx="22" cy="20" r="5" fill="#EF4444" />
      <circle cx="38" cy="20" r="5" fill="#F59E0B" />
      <circle cx="54" cy="20" r="5" fill="#22C55E" className="telemetry-pulse" />
      <text x="74" y="24" fill="#E2E8F0" fontSize="12" fontFamily="monospace" fontWeight="700">
        {agent.codeName} • FastMCP Deterministic Pipeline
      </text>

      {/* Node 1: Input FHIR / Clinical Signal */}
      <rect x="24" y="64" width="128" height="92" rx="8" fill="#1E293B" stroke="#475569" strokeWidth="1.5" />
      <text x="36" y="86" fill="#94A3B8" fontSize="10" fontFamily="monospace" fontWeight="700">
        STAGE 1 • INPUT
      </text>
      <text x="36" y="108" fill="#F8FAFC" fontSize="12" fontFamily="sans-serif" fontWeight="700">
        HL7 FHIR R4
      </text>
      <text x="36" y="126" fill="#CBD5E1" fontSize="10.5" fontFamily="sans-serif">
        {agent.fastMcpBadges[0]}
      </text>
      <rect x="36" y="136" width="84" height="10" rx="5" fill="#334155" />

      {/* Connector 1 */}
      <line x1="152" y1="110" x2="176" y2="110" stroke={accent} strokeWidth="2.5" strokeDasharray="4 3" />
      <polygon points="176,105 184,110 176,115" fill={accent} />

      {/* Node 2: FastMCP Guardrail Core */}
      <rect x="184" y="54" width="124" height="112" rx="10" fill="#0B2239" stroke={accent} strokeWidth="2" />
      <circle cx="292" cy="70" r="5" fill={accent} className="telemetry-pulse" />
      <text x="196" y="75" fill={accent} fontSize="10" fontFamily="monospace" fontWeight="700">
        FASTMCP :8081
      </text>
      <text x="196" y="98" fill="#FFFFFF" fontSize="12.5" fontFamily="sans-serif" fontWeight="800">
        Zero-Guess
      </text>
      <text x="196" y="115" fill="#FFFFFF" fontSize="12.5" fontFamily="sans-serif" fontWeight="800">
        Python Gate
      </text>
      <text x="196" y="135" fill="#BAE6FD" fontSize="10" fontFamily="monospace">
        {agent.capabilities[0].guardrailChip.slice(0, 18)}
      </text>
      <text x="196" y="151" fill="#94A3B8" fontSize="9.5" fontFamily="monospace">
        0% LLM Math
      </text>

      {/* Connector 2 */}
      <line x1="308" y1="110" x2="332" y2="110" stroke="#22C55E" strokeWidth="2.5" />
      <polygon points="332,105 340,110 332,115" fill="#22C55E" />

      {/* Node 3: Verified Clinical / Audit Output */}
      <rect x="340" y="64" width="116" height="92" rx="8" fill="#0F291E" stroke="#22C55E" strokeWidth="1.5" />
      <text x="352" y="86" fill="#86EFAC" fontSize="10" fontFamily="monospace" fontWeight="700">
        VERIFIED OUT
      </text>
      <text x="352" y="108" fill="#FFFFFF" fontSize="12" fontFamily="sans-serif" fontWeight="700">
        Signed R4
      </text>
      <text x="352" y="126" fill="#DCFCE7" fontSize="10" fontFamily="sans-serif">
        SHA-256 Audit
      </text>
      <text x="352" y="143" fill="#86EFAC" fontSize="9.5" fontFamily="monospace">
        PASS • 200 OK
      </text>

      {/* Bottom Telemetry Strip */}
      <rect x="24" y="184" width="432" height="92" rx="8" fill="#1E293B" stroke="#334155" strokeWidth="1" />
      <text x="38" y="206" fill="#94A3B8" fontSize="10" fontFamily="monospace" fontWeight="700">
        DETERMINISTIC GUARDRAIL TELEMETRY
      </text>
      <text x="38" y="228" fill="#F8FAFC" fontSize="11.5" fontFamily="monospace">
        ✓ {agent.fastMcpBadges[0]}   •   ✓ {agent.fastMcpBadges[1]}
      </text>
      <text x="38" y="250" fill="#38BDF8" fontSize="11" fontFamily="monospace">
        ✓ {agent.fastMcpBadges[2]}   •   ✓ Append-Only SQLite Ledger
      </text>
      <rect x="38" y="261" width="404" height="4" rx="2" fill="#0F172A" />
      <rect x="38" y="261" width="340" height="4" rx="2" fill={accent} />
    </svg>
  );
}

/**
 * 8 completely distinct bespoke SVG illustrations — each Vertical has its own visual motif & layout imagery.
 */
export function VerticalUniqueGraphic({
  variant,
  brand,
}: {
  variant: VerticalLayoutVariant;
  brand: string;
}) {
  switch (variant) {
    case 'resuscitation-command':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} acute resuscitation MTS and NEWS2 telemetry monitor`}>
          <rect width="460" height="280" rx="14" fill="#130912" stroke="#F87171" strokeWidth="2" />
          <text x="24" y="34" fill="#FCA5A5" fontSize="12" fontFamily="monospace" fontWeight="700">
            RESUS BAY 01 • MTS CAT 1 IMMEDIATE (0 MIN)
          </text>
          <circle cx="428" cy="29" r="6" fill="#EF4444" className="telemetry-pulse" />
          {/* ECG / NEWS2 Sparkline */}
          <polyline
            fill="none"
            stroke="#EF4444"
            strokeWidth="3"
            points="24,110 75,110 92,92 108,132 124,58 140,152 156,102 180,110 245,110 262,64 278,148 294,108 436,108"
          />
          <rect x="24" y="176" width="128" height="78" rx="8" fill="#2A101B" stroke="#F87171" />
          <text x="36" y="198" fill="#FCA5A5" fontSize="10" fontFamily="monospace">RCP NEWS2</text>
          <text x="36" y="232" fill="#FFFFFF" fontSize="26" fontFamily="sans-serif" fontWeight="800">9 / 20</text>
          <text x="36" y="247" fill="#FCA5A5" fontSize="10" fontFamily="sans-serif">HIGH SEPSIS ALERT</text>

          <rect x="166" y="176" width="128" height="78" rx="8" fill="#1E293B" stroke="#475569" />
          <text x="178" y="198" fill="#94A3B8" fontSize="10" fontFamily="monospace">VITALS (LOINC)</text>
          <text x="178" y="222" fill="#F8FAFC" fontSize="13" fontFamily="monospace" fontWeight="700">HR 132 • SpO2 89%</text>
          <text x="178" y="242" fill="#CBD5E1" fontSize="12" fontFamily="monospace">BP 88/54 • RR 28</text>

          <rect x="308" y="176" width="128" height="78" rx="8" fill="#0F291E" stroke="#4ADE80" />
          <text x="320" y="198" fill="#86EFAC" fontSize="10" fontFamily="monospace">3-TIER RX-GUARD</text>
          <text x="320" y="224" fill="#FFFFFF" fontSize="14" fontFamily="sans-serif" fontWeight="800">ACTIVE GATE</text>
          <text x="320" y="244" fill="#DCFCE7" fontSize="10.5" fontFamily="sans-serif">SHA-256 Provenance</text>
        </svg>
      );

    case 'longitudinal-care':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} GP clinic and mobile community nursing tablet view`}>
          <rect width="460" height="280" rx="14" fill="#0A253B" stroke="#38BDF8" strokeWidth="2" />
          {/* Tablet frame for Care-at-Home & GP */}
          <rect x="26" y="24" width="268" height="232" rx="12" fill="#FFFFFF" />
          <rect x="26" y="24" width="268" height="36" rx="12" fill="#0F172A" />
          <text x="42" y="47" fill="#38BDF8" fontSize="11" fontFamily="monospace" fontWeight="700">
            SlainteGP • Clinic &amp; Home Visit
          </text>
          <text x="42" y="84" fill="#0F172A" fontSize="13" fontFamily="sans-serif" fontWeight="800">
            Ambient Voice Scribe (SOAP)
          </text>
          <rect x="42" y="96" width="236" height="44" rx="6" fill="#F0F9FF" stroke="#BAE6FD" />
          <text x="52" y="115" fill="#0C4A6E" fontSize="10.5" fontFamily="sans-serif" fontWeight="700">
            S/O: Home visit BP 134/82, HbA1c 51 mmol/mol
          </text>
          <text x="52" y="131" fill="#334155" fontSize="10" fontFamily="sans-serif">
            Plan: Renew 28d Metformin (eGFR 68 CLEAR)
          </text>
          <rect x="42" y="152" width="112" height="38" rx="6" fill="#DCFCE7" />
          <text x="52" y="175" fill="#14532D" fontSize="11" fontFamily="sans-serif" fontWeight="700">✓ GMS Verified</text>
          <rect x="166" y="152" width="112" height="38" rx="6" fill="#E0F2FE" />
          <text x="176" y="175" fill="#0C4A6E" fontSize="11" fontFamily="sans-serif" fontWeight="700">✓ PCRS Ready</text>
          <rect x="42" y="204" width="236" height="34" rx="8" fill="#1B6B8D" />
          <text x="86" y="225" fill="#FFFFFF" fontSize="11.5" fontFamily="sans-serif" fontWeight="700">
            1-Tap Co-Sign to FHIR R4
          </text>

          {/* Smartphone companion for Community Nurse */}
          <rect x="314" y="54" width="120" height="202" rx="16" fill="#1E293B" stroke="#7DD3FC" strokeWidth="2" />
          <text x="330" y="82" fill="#BAE6FD" fontSize="9.5" fontFamily="monospace" fontWeight="700">HOME NURSE</text>
          <rect x="328" y="94" width="92" height="42" rx="6" fill="#0F172A" />
          <text x="336" y="113" fill="#FFFFFF" fontSize="10" fontFamily="sans-serif" fontWeight="700">44px Touch UI</text>
          <text x="336" y="128" fill="#38BDF8" fontSize="9.5" fontFamily="monospace">SpO2 98% • HR 74</text>
          <rect x="328" y="146" width="92" height="42" rx="6" fill="#0F172A" />
          <text x="336" y="165" fill="#86EFAC" fontSize="10" fontFamily="sans-serif" fontWeight="700">Rx-Guard Clear</text>
          <text x="336" y="180" fill="#CBD5E1" fontSize="9" fontFamily="sans-serif">Zero DDI Alerts</text>
          <rect x="328" y="218" width="92" height="24" rx="6" fill="#38BDF8" />
          <text x="342" y="234" fill="#0F172A" fontSize="9.5" fontFamily="sans-serif" fontWeight="800">Bottom Dock</text>
        </svg>
      );

    case 'therapeutic-calm':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} psychiatry MSE, PHQ-9 scales and GDPR Art. 9 compartment shield`}>
          <rect width="460" height="280" rx="14" fill="#191434" stroke="#A78BFA" strokeWidth="2" />
          <text x="26" y="38" fill="#DDD6FE" fontSize="12" fontFamily="monospace" fontWeight="700">
            SLAINTEPSYCH • CMHT &amp; PSYCHIATRIC SAFETY CONSOLE
          </text>
          <rect x="26" y="56" width="246" height="196" rx="10" fill="#261F4D" stroke="#8B5CF6" />
          <text x="42" y="82" fill="#FFFFFF" fontSize="13" fontFamily="sans-serif" fontWeight="800">
            LOINC Standardized Rating Scales
          </text>
          <text x="42" y="110" fill="#EDE9FE" fontSize="11.5" fontFamily="monospace">PHQ-9 (44261-6): 14 &rarr; 8 (Improving)</text>
          <rect x="42" y="120" width="210" height="8" rx="4" fill="#17153B" />
          <rect x="42" y="120" width="110" height="8" rx="4" fill="#A78BFA" />
          <text x="42" y="152" fill="#EDE9FE" fontSize="11.5" fontFamily="monospace">GAD-7 (70274-6): 11 &rarr; 6 (Mild)</text>
          <rect x="42" y="162" width="210" height="8" rx="4" fill="#17153B" />
          <rect x="42" y="162" width="84" height="8" rx="4" fill="#34D399" />
          <rect x="42" y="188" width="214" height="46" rx="6" fill="#17153B" />
          <text x="52" y="208" fill="#86EFAC" fontSize="10.5" fontFamily="monospace" fontWeight="700">✓ Renal eGFR &amp; Psychotropic Gate</text>
          <text x="52" y="224" fill="#CBD5E1" fontSize="10" fontFamily="sans-serif">Lithium / CNS Regimen Screened</text>

          {/* Confidentiality Shield */}
          <rect x="290" y="56" width="144" height="196" rx="10" fill="#120E29" stroke="#C4B5FD" />
          <circle cx="362" cy="112" r="30" fill="#3B1D5E" stroke="#C4B5FD" strokeWidth="2" />
          <text x="346" y="117" fill="#FFFFFF" fontSize="13" fontFamily="monospace" fontWeight="800">ART.9</text>
          <text x="308" y="166" fill="#FFFFFF" fontSize="12" fontFamily="sans-serif" fontWeight="700">BOLA Isolated</text>
          <text x="308" y="186" fill="#DDD6FE" fontSize="10.5" fontFamily="sans-serif">PII Redacted Before</text>
          <text x="308" y="202" fill="#DDD6FE" fontSize="10.5" fontFamily="sans-serif">AI Summarisation</text>
          <text x="308" y="230" fill="#FDE68A" fontSize="9.5" fontFamily="monospace">60m Break-Glass Audit</text>
        </svg>
      );

    case 'precision-odontogram':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} 32-tooth FDI Odontogram and pre-operative medical clearance`}>
          <rect width="460" height="280" rx="14" fill="#072227" stroke="#2DD4BF" strokeWidth="2" />
          <text x="24" y="36" fill="#99F6E4" fontSize="12" fontFamily="monospace" fontWeight="700">
            FDI 32-TOOTH ODONTOGRAM (11–48) &amp; PRE-OP CLEARANCE
          </text>
          {/* Upper Arch */}
          {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
            <g key={`u-${i}`}>
              <rect x={26 + i * 25} y="56" width="21" height="36" rx="5" fill={i === 5 ? '#FEE2E2' : '#CCFBF1'} stroke="#14B8A6" />
              <text x={30 + i * 25} y="78" fill="#0F172A" fontSize="9.5" fontFamily="monospace" fontWeight="800">{18 - i}</text>
              <rect x={236 + i * 25} y="56" width="21" height="36" rx="5" fill={i === 2 ? '#FEF3C7' : '#CCFBF1'} stroke="#14B8A6" />
              <text x={240 + i * 25} y="78" fill="#0F172A" fontSize="9.5" fontFamily="monospace" fontWeight="800">{21 + i}</text>
            </g>
          ))}
          {/* Lower Arch */}
          {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
            <g key={`l-${i}`}>
              <rect x={26 + i * 25} y="104" width="21" height="36" rx="5" fill="#E2E8F0" stroke="#14B8A6" />
              <text x={30 + i * 25} y="126" fill="#0F172A" fontSize="9.5" fontFamily="monospace" fontWeight="800">{48 - i}</text>
              <rect x={236 + i * 25} y="104" width="21" height="36" rx="5" fill={i === 5 ? '#DBEAFE' : '#E2E8F0'} stroke="#14B8A6" />
              <text x={240 + i * 25} y="126" fill="#0F172A" fontSize="9.5" fontFamily="monospace" fontWeight="800">{31 + i}</text>
            </g>
          ))}
          {/* Medical Clearance Gate */}
          <rect x="26" y="162" width="408" height="94" rx="10" fill="#0D363D" stroke="#5EEAD4" />
          <text x="42" y="188" fill="#FFFFFF" fontSize="13" fontFamily="sans-serif" fontWeight="800">
            Chairside Pre-Procedure Pharmacology &amp; Hemostasis Gate
          </text>
          <text x="42" y="212" fill="#FCA5A5" fontSize="11.5" fontFamily="monospace" fontWeight="700">
            ! BLOCK: Penicillin Allergy &rarr; Amoxicillin 500mg Intercepted
          </text>
          <text x="42" y="236" fill="#99F6E4" fontSize="11" fontFamily="monospace">
            ✓ 6-Sextant BPE: 2 / 1 / 2 | 3 / 1 / 2 &rarr; Saved to FHIR R4 Observation
          </text>
        </svg>
      );

    case 'dispensing-matrix':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} 3-tier pharmacy dispensing safety queue and PCRS export`}>
          <rect width="460" height="280" rx="14" fill="#071F15" stroke="#4ADE80" strokeWidth="2" />
          <text x="24" y="36" fill="#86EFAC" fontSize="12" fontFamily="monospace" fontWeight="700">
            PSI CLINICAL DISPENSING QUEUE • 3-TIER RX-GUARD
          </text>
          <rect x="24" y="54" width="412" height="58" rx="8" fill="#2C1215" stroke="#F87171" />
          <text x="38" y="76" fill="#FCA5A5" fontSize="11" fontFamily="monospace" fontWeight="700">
            TIER 2 HIGH-ALERT DDI • Rhabdomyolysis Risk
          </text>
          <text x="38" y="96" fill="#FFFFFF" fontSize="12" fontFamily="sans-serif" fontWeight="700">
            Clarithromycin 500mg + Atorvastatin 80mg &rarr; HELD FOR PRESCRIBER
          </text>

          <rect x="24" y="124" width="412" height="58" rx="8" fill="#291E09" stroke="#FBBF24" />
          <text x="38" y="146" fill="#FDE68A" fontSize="11" fontFamily="monospace" fontWeight="700">
            TIER 3 RENAL LAB GATE • LOINC eGFR 26 mL/min
          </text>
          <text x="38" y="166" fill="#FFFFFF" fontSize="12" fontFamily="sans-serif" fontWeight="700">
            Metformin 1000mg BD Contraindicated (eGFR &lt; 30) &rarr; INTERCEPTED
          </text>

          <rect x="24" y="194" width="412" height="62" rx="8" fill="#0E3624" stroke="#4ADE80" />
          <text x="38" y="218" fill="#86EFAC" fontSize="11" fontFamily="monospace" fontWeight="700">
            ✓ DISPENSED &amp; PSI SIGNED • HSE PCRS GMS OID VERIFIED
          </text>
          <text x="38" y="240" fill="#FFFFFF" fontSize="12" fontFamily="sans-serif">
            Monthly GMS Claim Batch CSV Ready (/enterprise/pcrs/export)
          </text>
        </svg>
      );

    case 'rugged-field-tablet':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} ruggedised ambulance paramedic tablet ePCR console`}>
          <rect width="460" height="280" rx="18" fill="#1C1917" stroke="#F59E0B" strokeWidth="4" />
          <rect x="16" y="16" width="428" height="248" rx="10" fill="#291D0E" stroke="#78350F" />
          <text x="32" y="44" fill="#FDE68A" fontSize="12" fontFamily="monospace" fontWeight="800">
            RUGGED FIELD ePCR TABLET • 44PX GLOVE TOUCH MODE
          </text>
          <circle cx="420" cy="39" r="6" fill="#F59E0B" className="telemetry-pulse" />
          {/* Big Touch Tiles */}
          <rect x="32" y="62" width="124" height="72" rx="8" fill="#0F172A" stroke="#F59E0B" />
          <text x="44" y="84" fill="#FDE68A" fontSize="10" fontFamily="monospace">BP / HR</text>
          <text x="44" y="114" fill="#FFFFFF" fontSize="20" fontFamily="monospace" fontWeight="800">84/52 • 135</text>

          <rect x="168" y="62" width="124" height="72" rx="8" fill="#0F172A" stroke="#F59E0B" />
          <text x="180" y="84" fill="#FDE68A" fontSize="10" fontFamily="monospace">SpO2 / RR</text>
          <text x="180" y="114" fill="#FFFFFF" fontSize="20" fontFamily="monospace" fontWeight="800">87% • 30</text>

          <rect x="304" y="62" width="124" height="72" rx="8" fill="#7F1D1D" stroke="#FCA5A5" />
          <text x="316" y="84" fill="#FEE2E2" fontSize="10" fontFamily="monospace">AUTO ACUITY</text>
          <text x="316" y="114" fill="#FFFFFF" fontSize="18" fontFamily="sans-serif" fontWeight="800">MTS CAT 1</text>

          <rect x="32" y="152" width="396" height="90" rx="10" fill="#B45309" />
          <text x="54" y="188" fill="#FFFFFF" fontSize="16" fontFamily="sans-serif" fontWeight="800">
            1-TAP PUSH HL7 FHIR R4 BUNDLE TO RECEIVING ED -&gt;
          </text>
          <text x="54" y="216" fill="#FEF3C7" fontSize="11.5" fontFamily="monospace">
            Sub-10ms Deterministic Scoring • Zero Re-Entry at Resus Bay
          </text>
        </svg>
      );

    case 'athletic-telemetry':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} athlete readiness telemetry and SCAT6 return-to-play clearance`}>
          <rect width="460" height="280" rx="14" fill="#08201B" stroke="#34D399" strokeWidth="2" />
          <text x="24" y="36" fill="#A7F3D0" fontSize="12" fontFamily="monospace" fontWeight="700">
            FIRST-TEAM SQUAD BIO-TELEMETRY &amp; SCAT6 CLEARANCE
          </text>
          {[
            { y: 56, name: 'Athlete #07 (Midfield)', vitals: 'HR 52 • SpO2 99% • NEWS2 0', status: 'CLEARED (SHA-256)', ok: true },
            { y: 118, name: 'Athlete #10 (Out-Half)', vitals: 'SCAT6 Post-HIA Day 6 Review', status: 'SIGNED BY TEAM MD', ok: true },
            { y: 180, name: 'Athlete #04 (Lock)', vitals: 'Compartment Isolation: BOLA PASS', status: '0 UNAUTHZ READS', ok: true },
          ].map((row, idx) => (
            <g key={idx}>
              <rect x="24" y={row.y} width="412" height="50" rx="8" fill="#0F2E27" stroke="#10B981" />
              <text x="38" y={row.y + 22} fill="#FFFFFF" fontSize="12.5" fontFamily="sans-serif" fontWeight="700">{row.name}</text>
              <text x="38" y={row.y + 40} fill="#A7F3D0" fontSize="10.5" fontFamily="monospace">{row.vitals}</text>
              <rect x="292" y={row.y + 12} width="130" height="26" rx="6" fill="#065F46" />
              <text x="302" y={row.y + 29} fill="#ECFDF5" fontSize="10" fontFamily="monospace" fontWeight="700">{row.status}</text>
            </g>
          ))}
          <text x="24" y="256" fill="#6EE7B7" fontSize="11" fontFamily="monospace">
            ✓ TUE &amp; NSAID Renal Gate Active • ✓ CompartmentDefinition/Patient Isolated
          </text>
        </svg>
      );

    case 'orbital-airgap':
      return (
        <svg viewBox="0 0 460 280" width="100%" height="auto" role="img" aria-label={`${brand} air-gapped deep-space local 3B autonomous medical bay`}>
          <rect width="460" height="280" rx="14" fill="#050816" stroke="#818CF8" strokeWidth="2" />
          <circle cx="380" cy="76" r="42" fill="#1E1B4B" stroke="#6366F1" strokeWidth="1.5" />
          <ellipse cx="380" cy="76" rx="64" ry="18" fill="none" stroke="#818CF8" strokeDasharray="4 3" />
          <circle cx="90" cy="48" r="2" fill="#E0E7FF" />
          <circle cx="240" cy="36" r="1.5" fill="#E0E7FF" />
          <circle cx="290" cy="94" r="2" fill="#818CF8" className="telemetry-pulse" />

          <text x="24" y="38" fill="#C7D2FE" fontSize="12" fontFamily="monospace" fontWeight="700">
            AIR-GAPPED HABITAT MEDICAL BAY • 0 BYTES EARTH UPLINK
          </text>
          <rect x="24" y="64" width="256" height="84" rx="10" fill="#111633" stroke="#6366F1" />
          <text x="38" y="88" fill="#FFFFFF" fontSize="13" fontFamily="sans-serif" fontWeight="800">
            Onboard Sovereign Stack
          </text>
          <text x="38" y="110" fill="#A5B4FC" fontSize="11" fontFamily="monospace">
            • Local Ollama 3B (Doggo / Lime)
          </text>
          <text x="38" y="130" fill="#A5B4FC" fontSize="11" fontFamily="monospace">
            • FastMCP :8081 + SlainteFHIR :8082
          </text>

          <rect x="24" y="164" width="412" height="90" rx="10" fill="#0F172A" stroke="#4F46E5" />
          <text x="38" y="190" fill="#86EFAC" fontSize="11.5" fontFamily="monospace" fontWeight="700">
            ✓ ALL 11 AUTONOMOUS AGENTS ACTIVE IN LOCAL AIR-GAP
          </text>
          <text x="38" y="214" fill="#E0E7FF" fontSize="12" fontFamily="sans-serif">
            EVA Hypoxia NEWS2 Drift Monitoring • Onboard Kit 3-Tier Rx-Guard
          </text>
          <text x="38" y="236" fill="#94A3B8" fontSize="10.5" fontFamily="monospace">
            Cryptographic Flight Surgeon Provenance Ready for Delayed Earth Sync
          </text>
        </svg>
      );
  }
}
