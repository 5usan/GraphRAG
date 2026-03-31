import os
import numpy as np
from core.graph import get_all_relavant_info_about_class
from fastapi import APIRouter, Depends
from sklearn.metrics.pairwise import cosine_similarity

from utils.logger import init_logger
from utils.app_state import get_app_state
from utils.prompts import generate_sparql_prompt
from utils.cq_utils import get_key_words_related_to_cq, get_relavant_classes_for_cq


logger = init_logger()

router = APIRouter()

@router.post("/get_competency_question")
def get_competency_question(competency_question: str, app_state=Depends(get_app_state)):
    try:
        cq = get_key_words_related_to_cq(competency_question)

        driver = app_state.neo4j_driver or None
        # get all nodes with all their properties from neo4j dataset
        classes = []
        with driver.session() as session:
            result = session.run(
                "MATCH (n) RETURN n.name AS name, n.bert_embedding AS bert_embedding, n.word2vec_embedding AS word2vec_embedding"
            )
            for record in result:
                classes.append(
                    {
                        "name": record["name"],
                        "bert_embedding": record["bert_embedding"],
                        "word2vec_embedding": record["word2vec_embedding"],
                    }
                )
        relavent_classes = get_relavant_classes_for_cq(cq, classes)
        for cls in relavent_classes:
            info = get_all_relavant_info_about_class(cls["name"])
            cls["info"] = info
        # generate prompt for the LLM to answer the competency question using the relevant classes and their information and return the prompt to the user
        prompt = generate_sparql_prompt(competency_question, relavent_classes)
        return {
            "status": "OK",
            "prompt": prompt,
        }
    except Exception as e:
        logger.error(f"Error occurred while saving competency question: {e}")
        return {"status": "ERROR", "message": str(e)}


@router.get("/get_all_relavant_info_about_class")
def get_all_relavant_info_about_class_api(
    class_name: str, ontology_name: str = "enslaved-v2", format="ttl"
):
    try:
        info = get_all_relavant_info_about_class(class_name, ontology_name, format)
        return {
            "status": "OK",
            "message": "Class information retrieved successfully!",
            "class_info": info,
        }
    except Exception as e:
        logger.error(f"Error occurred while retrieving class information: {e}")
        return {"status": "ERROR", "message": str(e)}
