import os
from fastapi import FastAPI
from rdflib import OWL, RDF, RDFS

from utils.logger import init_logger
from api.health_check_api import router as health_router
from api.ontology_related_api import router as ontology_router
from utils.graph import (
    connect_to_neo4j,
    close_neo4j_connection,
)

logger = init_logger()
app = FastAPI(title="Thesis going somewhere", version="1.0.0")

logger.info("Starting the FastAPI application.")

@app.on_event("startup")
async def startup():
    """Initialize database connection on app startup"""
    try:
        driver = connect_to_neo4j()
        app.state.neo4j_driver = driver
    except Exception as e:
        logger.error(f"Error occurred while connecting to Neo4j: {e}")


#Routers
app.include_router(health_router, tags=["Health Check"])
app.include_router(ontology_router, tags=["Ontology"])


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    try:
        if hasattr(app.state, "neo4j_driver"):
            close_neo4j_connection(app.state.neo4j_driver)
    except Exception as e:
        logger.error(f"Error occurred while closing Neo4j connection: {e}")
