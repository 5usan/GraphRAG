import os
from fastapi import APIRouter, Depends

from utils.logger import init_logger
from constants.constants import GRAPH_PATH
from utils.graph import get_neo4j_driver, init_graph, save_ontology_to_neo4j

logger = init_logger()

router = APIRouter()


@router.get("/save-ontology")
def save_ontology(
    ontology_name: str = "enslaved-v2",
    format: str = "ttl",
    driver=Depends(get_neo4j_driver),
):
    """
    Endpoint to save the ontology to Neo4j.
    """
    try:
        graph = init_graph()
        graph_path = os.path.join(GRAPH_PATH, f"{ontology_name}.{format}")
        graph_format = (
            "turtle" if format == "ttl" else format
        )  # Support for other formats need to be added
        graph.parse(graph_path, format=graph_format)
        logger.info("Graph initialized and data loaded successfully.")
        save_ontology_to_neo4j(driver, graph)

        return {"status": "OK", "message": "Ontology saved to Neo4j successfully!"}
    except Exception as e:
        logger.error(f"Error occurred while saving ontology: {e}")
        return {"status": "ERROR", "message": str(e)}
