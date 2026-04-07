# GraphRAG - Graph-based Retrieval-Augmented Generation

## Overview

GraphRAG is a thesis project that implements a Retrieval-Augmented Generation (RAG) framework using graph-based approaches. The project leverages ontologies, knowledge graphs, and embedding models to extract, structure, and query semantic information from RDF data sources.

## Features

- **RDF Ontology Processing**: Parse and process RDF and Turtle format ontologies
- **Graph Database Integration**: Store and query ontologies in Neo4j graph database
- **Semantic Embeddings**: Generate embeddings using BERT and Word2Vec models
- **FastAPI REST API**: Expose graph querying and processing capabilities via REST endpoints
- **Class Extraction**: Automatically extract and process classes from RDF ontologies
- **GPU Support**: Leverage CUDA for accelerated embedding generation

## Project Structure

```
.
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── Makefile                # Build and run targets
│   ├── constants/
│   │   └── constants.py        # Configuration constants (device, etc.)
│   ├── datasets/
│   │   ├── schema/             # RDF and ontology schema files
│   │   └── data/               # Data files
│   └── utils/
│       ├── graph.py            # RDF graph and Neo4j utilities
│       ├── logger.py           # Logging configuration
│       └── model.py            # Embedding model utilities
├── deliverables/               # Project deliverables and diagrams
├── meeting-minutes/            # Project meeting notes and progress
└── README.md
```

## Prerequisites

- Python 3.8+
- Neo4j Graph Database (local or remote)
- CUDA-capable GPU (optional, for accelerated processing)
- Required Python packages (see Installation)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GraphRAG
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn neo4j rdflib torch transformers gensim python-dotenv
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `src/` directory with Neo4j connection details:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```

## Usage

### Running the FastAPI Server

**Development mode** (with auto-reload):
```bash
cd src
make dev
```

**Production mode**:
```bash
cd src
make run
```

The API will be available at `http://localhost:8000`
API documentation available at `http://localhost:8000/docs`

### Available Make Commands

```bash
cd src
make help      # Show available commands
make dev       # Start server with auto-reload
make run       # Start production server
make clean     # Remove cache and build files
```

## Configuration

### Constants
- **Device**: Automatically detects and uses CUDA if available, otherwise falls back to CPU
  - Configured in `src/constants/constants.py`

### Neo4j Connection
Set the following environment variables:
- `NEO4J_URI`: Connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `password`)

## API Endpoints

Once running, the FastAPI application exposes REST endpoints for:
- Graph querying and traversal
- Ontology class extraction
- Semantic embedding generation
- Neo4j database operations

Access the interactive API documentation at `/docs` once the server is running.

## Architecture

- **RDF Graph Processing**: Uses RDFLib for parsing and managing RDF/OWL ontologies
- **Graph Database**: Neo4j stores and indexes the semantic graph
- **Embeddings**: BERT and Word2Vec models generate semantic embeddings for classes and properties
- **API Layer**: FastAPI provides RESTful access to all functionality

## Development

### Project Status
- Class extraction and embedding scripts implementation
- RAG framework development
- Neo4j integration and querying

### Contributing
This is a thesis project. For contributions or collaboration, please contact the project leads.

## Author

- **Susan Shrestha** - Thesis Author

## Acknowledgments

- Advisor: Cogan Shimizu
- Collaborators as listed in meeting minutes

## License

[Add appropriate license here]

## Contact

For questions or inquiries about this project, please contact the thesis advisor or author.
