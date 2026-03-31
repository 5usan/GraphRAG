import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from utils.logger import init_logger
from utils.app_state import get_app_state
from constants.constants import (
    PREPOSITIONS,
    ARTICLES,
    WH_QUESTIONS,
    VERBS,
    CONJUNCTIONS,
)
from utils.model import (
    load_pretrained_bert,
    get_bert_embedding,
)

logger = init_logger()


def get_key_words_related_to_cq(competency_question: str):
    try:
        cq = competency_question.split(" ")
        # remove punctuation from the competency question
        cq = [word.strip(".,!?;:()[]{}\"'") for word in cq]
        # remove prepositions, articles, wh questions, verbs, conjunctions and other stop words from the competency question
        prepositions = PREPOSITIONS
        articles = ARTICLES
        wh_questions = WH_QUESTIONS
        verbs = VERBS
        conjunctions = CONJUNCTIONS
        stop_words = prepositions + articles + wh_questions + verbs + conjunctions
        cq = [word for word in cq if word.lower() not in stop_words]
        # remove duplicates from the competency question
        cq = list(set(cq))
        # remove empty strings from the competency question
        cq = [word for word in cq if word != ""]
        return cq
    except Exception as e:
        logger.error(f"Error occurred while processing competency question: {e}")
        return []

def get_relavant_classes_for_cq(competency_question: str, classes: list):
    try:
        bert_model = load_pretrained_bert()
        relavent_classes = []
        for word in competency_question:
            # generate bert embedding for the word
            bert_embedding = np.array(get_bert_embedding(bert_model, word)).reshape(
                1, -1
            )
            for cls in classes:
                bert_similarity = cosine_similarity(
                    bert_embedding, np.array(cls["bert_embedding"]).reshape(1, -1)
                )
                if bert_similarity[0][0] > 0.95:
                    cls["name"] not in relavent_classes and relavent_classes.append(
                        cls["name"]
                    )

        return relavent_classes
    except Exception as e:
        logger.error(f"Error occurred while getting relevant classes for competency question: {e}")
        return []