from rdflib import Graph

from utils.logger import init_logger

logger = init_logger()

def init_graph():
    try:
        graph = Graph()
        logger.info("RDF graph initialized successfully.")
        return graph
    except Exception as e:
        logger.error(f"Error initializing RDF graph: {e}")
        return None
