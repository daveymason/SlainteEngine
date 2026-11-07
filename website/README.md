# SlaintePages — SlainteTech AI Security Labs Public Platform

Next.js 15 (`output: 'export'`) + Material UI (`@mui/material` v6) static public website for **SlainteTech AI Security Labs**, passing WCAG 2.2 AA contrast and responsive across desktop, clinical tablets, and smartphones.

## Route Architecture

- **`/`** — Startup Home Page featuring the **"For..." 8 Industry Verticals showcase**, 11 Autonomous Health-Tech Agents, responsive Care-at-Home & Ambulance Tablet UX callout, and buyer/investor paths.
- **`/health-tech-agents/`** & **`/health-tech-agents/<agent-real-name>/`** (11 canonical agent pages):
  - All 11 agents share the reusable [`AgentCanonicalTemplate.tsx`](src/components/AgentCanonicalTemplate.tsx):
    1. Hero + bespoke FastMCP architecture SVG (`AgentSchematicSvg`)
    2. 3-column deterministic capabilities & guardrails
    3. **Full-width Vertical Use Case Page Break** linked directly to its matching `/verticals/<slug>/` page
    4. Accessible HL7 FHIR R4 technical specification `<table>`
    5. **End-of-page 3-column solution grid** showcasing the other 10 autonomous agents
- **`/verticals/`** & **`/verticals/<domain>/`** (8 visually distinct vertical pages):
  - `emergency-departments`, `general-practice`, `psychiatry`, `dentistry`, `pharmacy`, `ambulance-ems`, `sports-medicine`, `astronaut-health`
  - Each vertical uses [`VerticalUniqueTemplate.tsx`](src/components/VerticalUniqueTemplate.tsx) with its own WCAG 2.2 AA verified palette, unique SVG graphic (`VerticalUniqueGraphic`), mobile/tablet readiness callout, 3-step workflow, and buyer/investor ROI brief.
- **Startup & Buyer Pages**: `/platform/`, `/security-compliance/`, `/pricing/`, `/investors/`, `/docs/`, `/about/`, `/contact/`, plus `/llms.txt` GEO manifest.

## Build & Local Preview

```bash
npm install
npm run build        # Static HTML/CSS/JS exported to ./public-site/
npm run start        # Serves ./public-site on http://localhost:3001
```
