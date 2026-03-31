import os
from neo4j import GraphDatabase
from rdflib import RDF, OWL, BNode, RDFS

from utils.logger import init_logger
from utils.graph_utils import init_graph
from constants.constants import GRAPH_PATH, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from utils.model import (
    get_bert_embedding,
    get_word2vec_embedding,
    load_pretrained_bert,
    load_pretrained_word2vec,
)

logger = init_logger()


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
    try:
        if driver:
            driver.close()
            logger.info("Neo4j connection closed successfully")
    except Exception as e:
        logger.error(f"Error occurred while closing Neo4j connection: {e}")


def save_ontology_to_neo4j(driver, graph):
    """Save RDF ontology to Neo4j database"""
    try:
        if not driver or not graph:
            logger.error("Driver or graph is None")
            return

        with driver.session() as session:
            # 1. Create class nodes
            create_class_nodes(session, graph)

            logger.info("Ontology saved to Neo4j successfully")
    except Exception as e:
        logger.error(f"Error occurred while saving ontology to Neo4j: {e}")


def create_class_nodes(session, graph):
    """Create owl:Class nodes in Neo4j"""
    classes = list(set(graph.subjects(RDF.type, OWL.Class)))
    logger.info(f"Found {len(classes)} classes in the RDF graph")
    word2vec_model = load_pretrained_word2vec()
    bert_model = load_pretrained_bert()
    for cls in classes:
        if isinstance(cls, BNode):
            logger.warning(f"Skipping blank node {cls} when creating class nodes")
            continue
        class_name = str(cls).split("/")[-1]  # Get the local name of the class
        class_uri = str(cls)
        word2vec_embedding = get_word2vec_embedding(word2vec_model, class_name)
        bert_embedding = get_bert_embedding(bert_model, class_name)
        if word2vec_embedding is None or bert_embedding is None:
            logger.warning(f"Could not generate embeddings for class '{class_name}'")
            continue
        session.run(
            """
            MERGE (c:Class {uri: $uri})
            SET c.name = $name,
            c.word2vec_embedding = $word2vec_embedding,
            c.bert_embedding = $bert_embedding 
            """,
            uri=class_uri,
            name=class_name,
            word2vec_embedding=word2vec_embedding,
            bert_embedding=bert_embedding,
        )
    logger.info(f"Created {len(classes)} Class nodes in Neo4j")


def get_all_relavant_info_about_class(
    class_name, ontology_name: str = "enslaved-v2", format="ttl"
):
    """Get all relevant information about a class from ontology file"""
    try:
        graph = init_graph()
        graph_path = os.path.join(GRAPH_PATH, f"{ontology_name}.{format}")
        graph_format = "turtle" if format == "ttl" else format
        graph.parse(graph_path, format=graph_format)

        classes = list(set(graph.subjects(RDF.type, OWL.Class)))
        class_uri = None

        for cls in classes:
            if str(cls).split("/")[-1] == class_name:
                class_uri = cls
                break
        else:
            logger.warning(f"Class '{class_name}' not found in ontology")
            return None

        class_info = {
            "name": [class_name],
            "comment": [],
            "properties": [],  # Store all properties with constraints
            "sub_class_of": [],
            "sub_classes": [],
        }

        # Extract all predicates and objects
        for predicate, obj in graph.predicate_objects(subject=class_uri):
            pred_name = str(predicate).split("/")[-1]

            # Extract comments
            if pred_name in ["comment", "label", "description"]:
                class_info["comment"].append(str(obj))

            # Extract superclasses with restrictions
            if isinstance(obj, BNode):
                # Extract restriction details
                restriction = extract_restriction(graph, obj)
                if restriction:
                    class_info["properties"].append(restriction)
            else:
                obj_name = str(obj).split("/")[-1]
                if pred_name == "rdf-schema#subClassOf":
                    class_info["sub_class_of"].append(obj_name)

        # Find subclasses
        subclasses = list(graph.subjects(RDFS.subClassOf, class_uri))
        for subclass in subclasses:
            if not isinstance(subclass, BNode):
                subclass_name = str(subclass).split("/")[-1]
                class_info["sub_classes"].append(subclass_name)

        logger.info(f"Retrieved information for class '{class_name}'")
        return class_info

    except Exception as e:
        logger.error(f"Error occurred while getting class info from ontology: {e}")
        return None


def extract_restriction(graph, blank_node):
    """Extract all constraints from an OWL restriction (blank node)"""
    restriction = {}
    for pred, obj in graph.predicate_objects(subject=blank_node):
        pred_name = str(pred).split("/")[-1]
        obj_name = str(obj).split("/")[-1] if "/" in str(obj) else str(obj)
        restriction[pred_name] = obj_name
    return restriction if restriction else None
