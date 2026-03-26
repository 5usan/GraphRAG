import os
from dotenv import load_dotenv
from rdflib import OWL, RDF, RDFS
from fastapi import FastAPI
from neo4j import GraphDatabase

from utils.logger import init_logger
from utils.graph import init_graph, connect_to_neo4j, close_neo4j_connection, save_ontology_to_neo4j

load_dotenv()
logger = init_logger()
app = FastAPI(title="Thesis going somewhere", version="1.0.0")

logger.info("Starting the FastAPI application.")

graph = init_graph()
graph.parse("./datasets/schema/enslaved-v2.ttl", format="turtle")
logger.info("Graph initialized and data loaded successfully.")

driver = None

@app.on_event("startup")
async def startup():
    """Initialize database connection on app startup"""
    global driver
    driver = connect_to_neo4j()
    #Save classes of an ontology to Neo4j on startup
    # save_ontology_to_neo4j(driver, graph)


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    close_neo4j_connection(driver)