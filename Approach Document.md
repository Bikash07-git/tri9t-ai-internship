# Approach Document – Tri9T Engineering Assignment

## 1. Document Parsing & Hierarchy Reconstruction

To parse the technical manuals, I selected **PyMuPDF (fitz)** because it provides reliable access to document metadata such as font size, formatting, and page structure, enabling accurate hierarchy reconstruction without relying solely on visual layout.

### Hierarchy Reconstruction Strategy
- Implemented a **stack-based hierarchy builder** (`current_parents`) to maintain parent-child relationships between document sections.
- Mapped document structure based on font sizes:
  - **16.5 pt** → Heading Level 1 (H1)
  - **12.9 pt** → Heading Level 2 (H2)
  - **11.0 pt** → Body text
- Each extracted node is assigned a logical hierarchy before being stored in the database.

### Edge Case Handling
During development, I identified a formatting inconsistency in **Section 2.1.1.1 (Battery Life)** where the heading used the same font size as regular body text. Relying solely on font size would incorrectly classify it as a paragraph.

To improve robustness, I introduced a **regular-expression fallback** (`^\d+\.\d+\.\d+`) that detects numbered section patterns, ensuring correct hierarchy reconstruction even when formatting is inconsistent.

---

## 2. Versioning & Document Matching Strategy

### Data Model
The backend uses **SQLite** with **SQLAlchemy ORM** to manage versioned document storage. Every extracted document node is associated with a specific **version_id**, enabling multiple versions of the same manual to coexist.

### Staleness Detection
Each document node is assigned a **SHA-256 content hash** generated from its textual content.

When a new document version is ingested:

- Nodes are matched using a persistent **logical_node_id**.
- Content hashes are compared between document versions.
- If the hashes differ, the corresponding node is automatically marked as **stale**, indicating that previously generated test cases may no longer be valid.

This approach enables efficient change detection without performing expensive text comparisons.

---

## 3. LLM Integration Strategy

To ensure reliability during development, I implemented a **mock LLM generator** that simulates structured test-case generation.

In a production environment, this component can be replaced with an external LLM provider such as **Gemini** or **Groq**.

To prevent invalid outputs from entering the system:

- LLM responses are validated using **Pydantic schemas**.
- JSON parsing is wrapped in structured **try/except** blocks.
- Invalid or malformed responses result in an appropriate API error rather than being stored.

This validation layer protects downstream services from corrupted AI-generated data.

---

# Decision Log

## 1. What part of the system is most likely to silently produce incorrect results?

The **document parser** is the component most susceptible to silent failures.

If a future document introduces a new formatting style—for example, an 11 pt bold heading without hierarchical numbering—the parser may incorrectly classify it as body text while still completing successfully.

To mitigate this risk, I would implement automated parser validation tests that compare the extracted hierarchy against known baseline documents and verify the expected number of headings before ingestion.

---

## 2. Where did you prioritize simplicity over correctness?

To reduce implementation complexity within the assignment timeline, I stored generated test cases in a local JSON file (`test_cases_store.json`) instead of using a dedicated NoSQL database such as MongoDB.

While this solution is sufficient for a single-user prototype, it would not scale well in production.

Potential limitations include:

- Concurrent write conflicts
- File-locking issues
- Increased risk of data corruption under multiple simultaneous requests

A production deployment should replace this with a transactional database or document store.

---

## 3. What important input is currently unsupported?

The current implementation does not fully support **complex table extraction**.

Tables—such as the **Error Codes** section—are currently processed as sequential text rather than preserving their row-column relationships.

As a result:

- Table structure is lost.
- Cell relationships are not maintained.
- Generated test cases may lack the intended tabular context.

A production-ready solution would incorporate dedicated table extraction techniques or specialized PDF layout analysis libraries to accurately reconstruct structured tables.
