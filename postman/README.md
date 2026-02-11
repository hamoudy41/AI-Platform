# Postman – AI Platform

**Import in Postman:**

1. **Collection:** File → Import → select `AI-Platform.postman_collection.json`
2. **Environment (optional):** File → Import → select `AI-Platform.postman_environment.json`, then choose "AI Platform – Local" in the environment dropdown

**Variables (set in collection or environment):**

| Variable    | Default               | Description                                                         |
|------------|------------------------|---------------------------------------------------------------------|
| `base_url` | `http://localhost:8000` | API base URL                                                        |
| `tenant_id`| `tenant-123`          | Value for header `X-Tenant-ID`                                      |
| `doc_id`   | Auto per run          | Unique document id for Create/Get/Summarize; set by Create prerequest |

**Endpoints in the collection:**

- **Health** – GET health check
- **Documents** – POST create document, GET document by id
- **AI – Notary** – POST summarize (inline text), POST summarize (by document_id)
- **AI – Classify** – POST classify text
- **AI – Ask** – POST Q&A from context

**Run order:** Start the app with `uvicorn app.main:app --reload`, then run the collection. The Create document request uses a unique `doc_id` per run, so repeated runs avoid duplicate-key 500 errors. Summarize (by document_id) uses the same `doc_id` created in that run.
