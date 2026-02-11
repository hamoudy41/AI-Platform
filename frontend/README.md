# Frontend

React + TypeScript, Tailwind. Health, documents, classify, notary, ask.

```bash
npm install
npm run dev       # localhost:5173
npm test
npm run build
```

`VITE_API_BASE` overrides API URL. Standalone UI: `docker build -t ai-platform-ui .` (nginx serves SPA, proxies /api to the API service).
