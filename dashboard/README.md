# Tender Intelligence Dashboard

React + TypeScript + Vite + Tailwind v4 dashboard for the Tender Intelligence Platform API.

## Setup

```
npm install
cp .env.example .env
```

Edit `.env` if your API isn't running on the default `http://127.0.0.1:8000`.

## Run

```
npm run dev
```

Opens on `http://localhost:5173` — already allow-listed in the backend's CORS config.

## Pages

- `/` — aggregate stats (total, qualified, filtered out, not eligible, review required, unevaluated)
- `/tenders` — filterable, sortable, paginated tender list
- `/tenders/:tenderId` — full tender detail + evaluation transparency (matched/excluded keywords, passed/failed/unknown rules, reasons)

## Build

```
npm run build
```
