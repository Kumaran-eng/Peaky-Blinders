# DocTrust AI

## Trusted Document-Grounded Knowledge Assistant

DocTrust AI is an AI-powered document question-answering system that allows users to ask natural-language questions about a given set of documents.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from the provided documents and uses a Large Language Model through the Groq API to generate answers.

The most important feature of DocTrust AI is that it does not rely on outside knowledge when answering questions. If the required information cannot be found in the provided documents, the system clearly responds:

> "I don't know based on the provided documents."

This helps reduce hallucinations and makes the chatbot more trustworthy and suitable for knowledge-base applications.

---

# 1. Problem Statement

Organizations such as colleges, institutions, and companies maintain large amounts of information in documents such as:

- Handbooks
- FAQs
- Rules and regulations
- Policies
- Academic documents
- Student guidelines
- Knowledge-base documents

Users often find it difficult to search through these documents manually.

Traditional chatbots may also generate incorrect information because they use general AI knowledge instead of the organization's actual documents.

Therefore, there is a need for a system that:

1. Accepts organization-provided documents.
2. Understands the content of those documents.
3. Allows users to ask questions naturally.
4. Retrieves the most relevant information.
5. Generates answers only from the provided content.
6. Clearly says when the answer is not available.
7. Shows the source used for the answer.

---

# 2. Proposed Solution

DocTrust AI provides a document-grounded AI assistant.

The system processes the provided documents, divides them into smaller chunks, converts those chunks into vector embeddings, and stores them in a FAISS vector database.

When the user asks a question:

1. The question is converted into an embedding.
2. FAISS searches for similar document chunks.
3. The system checks the relevance of the retrieved information.
4. Relevant content is provided to the Groq LLM.
5. The LLM generates an answer using only the provided context.
6. The source document and page number are returned.
7. If sufficient information is unavailable, the system responds that it does not know the answer.

---

# 3. Key Features

## 3.1 Document Upload

Administrators can upload supported documents such as:

- PDF
- DOCX
- TXT

Uploaded documents are automatically processed and indexed.

---

## 3.2 Document Processing

The system extracts text from uploaded documents.

For PDF files, PyMuPDF is used.

For DOCX files, python-docx is used.

For TXT files, Python's built-in file handling is used.

---

## 3.3 Intelligent Chunking

Large documents are divided into smaller meaningful text chunks.

This improves retrieval accuracy and allows the AI model to focus on the most relevant information.

---

## 3.4 Semantic Search

The system uses Sentence Transformers to convert document chunks and user questions into numerical vector representations.

FAISS is then used to find the most relevant chunks.

---

## 3.5 RAG-Based Question Answering

DocTrust AI uses Retrieval-Augmented Generation.

The system does not directly ask the LLM to answer from its general knowledge.

Instead:

User Question
→ Retrieval
→ Relevant Document Content
→ LLM
→ Grounded Answer

---

## 3.6 Hallucination Protection

The system is designed to prevent unsupported answers.

The LLM is instructed to:

- Use only the retrieved context.
- Never guess.
- Never invent information.
- Never use outside knowledge.
- Clearly state when information is unavailable.

If the system cannot find sufficient evidence, it returns:

> "I don't know based on the provided documents."

---

## 3.7 Source Citations

Every grounded answer can include source information such as:

- Document name
- Page number
- Retrieval score

Example:

```text
Answer:
The library is open from 8 AM to 6 PM on weekdays.

Source:
college_handbook.pdf
Page: 12