\# Approach Document - Tri9T Engineering Assignment



\## 1. Document Parsing \& Hierarchy Reconstruction

I chose \*\*PyMuPDF (fitz)\*\* because it allows for deep inspection of document properties, specifically text size, without relying on unreliable visual layouts.

\* \*\*Hierarchy Strategy:\*\* I used a stack-based approach (`current\_parents`) tied to font sizes. Level 1 (H1) was mapped to 16.5pt font, Level 2 (H2) to 12.9pt, and body text to 11.0pt. 

\* \*\*Edge Case Handling:\*\* I discovered a structural inconsistency in Section 2.1.1.1 (Battery Life). Its font size (11.0pt) was identical to normal body text, which would mis-parent it. I mitigated this by adding a Regex fallback (`^\\d+\\.\\d+\\.\\d+`) to catch explicit numbering schemes alongside font size checks.



\## 2. Versioning and Matching Strategy

\* \*\*Data Model:\*\* I utilized SQLAlchemy with an SQLite backend. Nodes are tied to a `version\_id`. 

\* \*\*Staleness Tracking:\*\* I implemented a `content\_hash` (SHA-256) generated from the text of each node. When Version 2 is ingested, the system links the new node to the old node via a persistent `logical\_node\_id`. If the hashes mismatch, the system immediately flags the traceability as stale. 



\## 3. LLM Strategy

To handle malformed LLM outputs effectively, I implemented a mocking function during development. In a production environment, this function would wrap the actual API call (e.g., Groq/Gemini) in a strict `try/except` block utilizing Pydantic's structured output validation. If the LLM returns invalid JSON, the system is designed to raise a 502 error rather than saving corrupted data to the JSON store.



\## 4. Decision Log



\* \*\*What's the one part of this system most likely to silently give wrong results without erroring? How would you catch it?\*\*

&#x20; The parser. If a new version introduces a completely novel formatting style (e.g., bolded 11pt text acting as a heading without numbering), it would silently be logged as a standard paragraph. I would catch this by implementing an automated unit test that counts the expected number of H1/H2 nodes against known baseline documents before full database ingestion.

&#x20; 

\* \*\*Where did you choose simplicity over correctness because of time, and what would break first if this went to production as-is?\*\*

&#x20; I chose to store the AI-generated test cases in a local JSON file (`test\_cases\_store.json`) rather than deploying a full NoSQL cluster like MongoDB. If this went to production, concurrent write operations from multiple users hitting the generation API simultaneously would cause file-locking errors and data corruption.



\* \*\*Name one input that you did not handle, and what your system does when it sees it.\*\*

&#x20; I did not handle complex table extraction (like the Error Codes table in Section 4.2). Currently, my system reads tables sequentially line-by-line, treating table cells as a mashed-together body paragraph.

