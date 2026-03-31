import os
import numpy as np
from fastapi import APIRouter, Depends
from sklearn.metrics.pairwise import cosine_similarity

from utils.logger import init_logger
from utils.app_state import get_app_state
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
        print(relavent_classes)
        return {
            "status": "OK",
            "message": "Competency question saved successfully!",
            "relevant_classes": relavent_classes,
        }
    except Exception as e:
        logger.error(f"Error occurred while saving competency question: {e}")
        return {"status": "ERROR", "message": str(e)}
