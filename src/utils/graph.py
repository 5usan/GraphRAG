import os
from neo4j import GraphDatabase
from rdflib import Graph, RDF, OWL

from utils.logger import init_logger
from constants.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from utils.model import (
    get_bert_embedding,
    get_word2vec_embedding,
    load_pretrained_bert,
    load_pretrained_word2vec,
)

logger = init_logger()


def get_neo4j_driver():
    from main import app

    return app.state.neo4j_driver


def init_graph():
    try:
        graph = Graph()
        logger.info("RDF graph initialized successfully.")
        return graph
    except Exception as e:
        logger.error(f"Error initializing RDF graph: {e}")
        return None


def connect_to_neo4j():
    try:
        neo4j_uri = NEO4J_URI
        neo4j_user = NEO4J_USER
        neo4j_password = NEO4J_PASSWORD
        logger.info(f"Connecting to Neo4j at {neo4j_uri} with user {neo4j_user}")
        driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
        )
        driver.verify_connectivity()
        logger.info("Neo4j connection verified successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return None


def close_neo4j_connection(driver):
    if driver:
        driver.close()
        logger.info("Neo4j connection closed successfully")


def save_ontology_to_neo4j(driver, graph):
    """Save RDF ontology to Neo4j database"""
    if not driver or not graph:
        logger.error("Driver or graph is None")
        return

    with driver.session() as session:
        # 1. Create class nodes
        create_class_nodes(session, graph)

        logger.info("Ontology saved to Neo4j successfully")


def create_class_nodes(session, graph):
    """Create owl:Class nodes in Neo4j"""
    classes = list(set(graph.subjects(RDF.type, OWL.Class)))
    logger.info(f"Found {len(classes)} classes in the RDF graph")
    word2vec_model = load_pretrained_word2vec()
    bert_model = load_pretrained_bert()
    for cls in classes:
        class_name = str(cls).split("/")[-1]  # Get the local name of the class
        class_uri = str(cls)
        word2vec_embedding = get_word2vec_embedding(word2vec_model, class_name)
        bert_embedding = get_bert_embedding(bert_model, class_name)

        session.run(
            """
            MERGE (c:Class {uri: $uri})
            SET c.name = $name,
            c.word2vec_embedding = $word2vec_embedding,
            c.bert_embedding = $bert_embedding 
            """,
            uri=class_uri,
            name=class_name,
            word2vec_embedding=word2vec_embedding,  # Placeholder for future embedding
            bert_embedding=bert_embedding,  # Placeholder for future embedding
        )
    logger.info(f"Created {len(classes)} Class nodes in Neo4j")
