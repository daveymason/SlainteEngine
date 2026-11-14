# SlaintePages — SlainteTech AI Security Labs Public Platform

Production website: **https://slainte-tech.com/**  
Contact email: **`hello@slainte-tech.com`**

Next.js 15 (`output: 'export'`) + Material UI (`@mui/material` v6) static public website for **SlainteTech AI Security Labs**, passing WCAG 2.2 AA contrast and responsive across desktop, clinical tablets, and smartphones.

## Route Architecture

- **`/`** — Startup Home Page featuring the **"For..." 8 Industry Verticals showcase**, 16 Autonomous Health-Tech Agents, responsive Care-at-Home & Ambulance Tablet UX callout, clinical environment photography, and buyer/investor paths.
- **`/health-tech-agents/`** & **`/health-tech-agents/<agent-real-name>/`** (16 canonical agent pages):
  - All 16 agents share the reusable [`AgentCanonicalTemplate.tsx`](src/components/AgentCanonicalTemplate.tsx):
    1. Hero + bespoke FastMCP architecture SVG (`AgentSchematicSvg`)
    2. 3-column deterministic capabilities & guardrails
    3. **Full-width Vertical Use Case Page Break** linked directly to its matching `/verticals/<slug>/` page
    4. Accessible HL7 FHIR R4 technical specification `<table>`
    5. **End-of-page 3-column solution grid** showcasing the other 15 autonomous agents
- **`/verticals/`** & **`/verticals/<domain>/`** (8 visually distinct vertical pages):
  - `emergency-departments`, `general-practice`, `psychiatry`, `dentistry`, `pharmacy`, `ambulance-ems`, `sports-medicine`, `astronaut-health`
  - Each vertical uses [`VerticalUniqueTemplate.tsx`](src/components/VerticalUniqueTemplate.tsx) with its own WCAG 2.2 AA verified palette, unique SVG graphic (`VerticalUniqueGraphic`), mobile/tablet readiness callout, 3-step workflow, and buyer/investor ROI brief.
- **Startup, Buyer & SEO Assets**: `/platform/`, `/security-compliance/`, `/pricing/`, `/investors/`, `/docs/`, `/about/`, `/contact/`, `/sitemap.xml`, `/robots.txt`, and `/llms.txt` GEO manifest.

## Build & Local Preview

```bash
npm install
npm run build        # Static HTML/CSS/JS exported to ./public-site/
npm run start        # Serves ./public-site on http://localhost:3001
```

## Production CI/CD: GitHub Pages + Hostinger DNS & Email

GitHub Actions (`.github/workflows/deploy-pages.yml`) builds and deploys `./public-site/` automatically on every push to `main`. `public/.nojekyll` prevents Jekyll from stripping `/_next/` assets, and `public/CNAME` binds the custom domain `slainte-tech.com`.

### Hostinger DNS Records (keep existing Hostinger `MX` / `SPF` / `DKIM` / `DMARC` records untouched for `hello@slainte-tech.com`)

1. **Apex (`@`) `A` records** pointing to GitHub Pages:
   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`
2. **Apex (`@`) `AAAA` records** (IPv6, recommended):
   - `2606:50c0:8000::153`
   - `2606:50c0:8001::153`
   - `2606:50c0:8002::153`
   - `2606:50c0:8003::153`
3. **`www` `CNAME` record**:
   - Host: `www` → Target: `daveymason.github.io`
4. **GitHub Repository Settings → Pages**:
   - **Source**: `GitHub Actions`
   - **Custom domain**: `slainte-tech.com`
   - **Enforce HTTPS**: Enabled once DNS propagates
