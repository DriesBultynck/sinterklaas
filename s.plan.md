# Plan: Add Pay-Per-Use Payments

## Scope
Binnen de `projects/sinterklaas` folder een geïntegreerd betaal- en credit-systeem bouwen zodat elke gebruiker €1 betaalt voor 5 generaties (audio/brief) en daarna automatisch wordt geblokkeerd tot de volgende betaling.

## Steps

1. **Backend mini-service binnen sinterklaas**
   - Maak een subfolder `projects/sinterklaas/backend` met een lichte API (FastAPI/Flask) en database/tabellen `user_credits`, `usage_logs`, `payments` (bv. SQLite of Supabase client).
   - Endpoints: `POST /credits/use`, `GET /credits/status`, `POST /payments/create`, `POST /payments/webhook`.
   - Zorg dat `credits/use` atomair 1 credit aftrekt en elke actie logt in `usage_logs`.

2. **Betaalintegratie (Stripe of Payconiq)**
   - Voeg in `projects/sinterklaas/backend/payments.py` een service toe die een €1 checkout sessie (QR-compatibel) aanmaakt en metadata koppelt aan de gebruiker.
   - Webhook validatie: bij succesvolle betaling `payments` updaten en +5 credits in `user_credits` schrijven.
   - Houd structuur modulair zodat later Payconiq of andere providers kunnen worden toegevoegd.

3. **Streamlit app updates**
   - Pas `projects/sinterklaas/app.py` aan om gebruikers te identificeren (bv. e-mail input) en een token/session met de backend te behouden.
   - Voor elk audio/brief verzoek eerst `GET /credits/status`; bij 0 credits toon een betaalcall-to-action met QR/checkout link.
   - Na betaling poll `GET /credits/status` tot credits beschikbaar zijn en toon resterende credits in de UI.

4. **Beveiliging & UX**
   - Alle creditvalidatie gebeurt server-side; de UI toont alleen status.
   - Voeg foutafhandeling, timeouts en logging toe (rate limiting via `usage_logs`).
   - Documenteer de flow en setup in `projects/sinterklaas/README.md`.

## Todos
- `sint-backend`: Backend subfolder + credit/payment tabellen & endpoints.
- `sint-payments`: Stripe/Payconiq checkout + webhook integreren.
- `sint-app-ui`: Streamlit app.py aanpassen voor credit checks en betaalflow.
- `sint-docs-tests`: Documentatie en basis tests/manual QA.

