# avsRAG 🧠🗃️

(a very simple)RAG is a basic Retrieval-Augmented Generation application that implements a simple RAG pipeline using a vector database and a language model.

## Features
- **Language Model**: Integrates with ollama's language models for generating responses.
- **Simple Interface**: Provides a straightforward interface for querying and retrieving information.
- **Document Management**: Allows for adding and managing documents in the vector database.
- **Vector Database**: [ ! ] Currently working on implementing Postgres pgvector support.

# To-Do
- [x] Implement Ollama language model support.
- [x] Implement simple query interface.
- [ ] Implement simple vector database interface.
- [ ] Implement simple document upload interface.
- [ ] Implement simple document management.
- [ ] Implement Postgres pgvector support.

## 🚀 Quickstart

**Clone & install main CLI runner**  
  ```bash
  git clone https://github.com/nicosept/avsRAG.git

  # Virtual environments are good practice!
  python3 -m venv .venv
  source .venv/bin/activate # OR .venv\Scripts\activate for Windows

  pip install -e .
  ```

**Install duo server dependencies**  
  ```bash
  # Backend
  cd ./backend
  pip install .

  # Frontend
  cd ./frontend
  npm install
  ```

**Run the application with:**  
  ```bash
  avsrag run
  ```
<br>

**External dependencies**  
  - [Ollama](https://ollama.com/) for language model support.
  - [Postgres](https://www.postgresql.org/) with pgvector for vector database support. (Not yet required)



## Future Work
- **Multiple LLM API support**: Add support for more language models starting with OpenAI.
- **Multiple Vector Database support**: Implement support for multiple vector databases.
