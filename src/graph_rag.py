import logging
import argparse

from api.CQs_related_api import generate_prompt_for_multiple_cq_api

parser = argparse.ArgumentParser(
    description="GraphRAG: A Retrieval-Augmented Generation Approach for Question Answering over Knowledge Graphs"
)

parser.add_argument("-o", "--ontology_path", help="Path to the ontology file")

parser.add_argument(
    "-cq", "--cq_file_path", help="Path to the competency questions file"
)

parser.add_argument(
    "-out", "--output-dir", default="output", help="Directory to write output files"
)

parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)"
)

parser.add_argument("--log-file", help="Log file name (if omitted, logs go to stderr)")

cli_args = parser.parse_args()

# Set up and configure logging
log_level = logging.DEBUG if cli_args.verbose else logging.WARNING

logging_kwargs = {
    "level": log_level,
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}

if cli_args.log_file:
    logging_kwargs["filename"] = cli_args.log_file
    logging_kwargs["filemode"] = "w"  # Overwrite log file on each run


logging.basicConfig(**logging_kwargs)

logger = logging.getLogger(__name__)

ontology_path = cli_args.ontology_path
cq_file_path = cli_args.cq_file_path
output_dir = cli_args.output_dir

logger.info(f"Ontology path: {ontology_path}")

response = generate_prompt_for_multiple_cq_api(
    file_name=None,
    graph_path=ontology_path,
    file_path=cq_file_path,
    output_path=output_dir,
    app_state=None,
)
logger.info(response["message"])

# Usage:
# python graph_rag.py
#   -o path/to/ontology.owl
#   -cq path/to/cqs.txt
#   -out output_directory
#   -v
#   --log-file graph_rag.log
