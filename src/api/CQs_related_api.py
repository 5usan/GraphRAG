import os
import json

from utils.logger import init_logger

logger = init_logger()
try:
    from fastapi import APIRouter, Depends
except ImportError:
    # if fastapi is not installed, thats fine
    APIRouter = None
    Depends = None
    logger.warning(
        "FastAPI is not installed. API routes will not be available. I guess a script is running which doesn't require FastAPI, so it's fine. If you want to use the API routes, please install FastAPI."
    )

from utils.app_state import get_app_state
from constants.constants import DATA_PATH
from utils.prompts import generate_sparql_prompt
from core.graph import get_all_relavant_info_about_class, get_namespaces
from utils.cq_utils import get_key_words_related_to_cq, get_relavant_classes_for_cq

router = APIRouter()

# Need to fix this api
@router.post("/get_competency_question")
def get_competency_question(
    competency_question: str, graph_path: str, app_state=Depends(get_app_state)
):
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
        prefix_namespaces = get_namespaces(graph_path)
        for cls in relavent_classes:
            info = get_all_relavant_info_about_class(cls["name"], graph_path)
            cls["info"] = info
        # generate prompt for the LLM to answer the competency question using the relevant classes and their information and return the prompt to the user
        context = generate_sparql_prompt(
            competency_question, relavent_classes, prefix_namespaces
        )
        return {
            "status": "OK",
            "context": context,
        }
    except Exception as e:
        logger.error(f"Error occurred while saving competency question: {e}")
        return {"status": "ERROR", "message": str(e)}


@router.get("/get_all_relavant_info_about_class")
def get_all_relavant_info_about_class_api(class_name: str, graph_path: str):
    try:
        info = get_all_relavant_info_about_class(class_name, graph_path)
        return {
            "status": "OK",
            "message": "Class information retrieved successfully!",
            "class_info": info,
        }
    except Exception as e:
        logger.error(f"Error occurred while retrieving class information: {e}")
        return {"status": "ERROR", "message": str(e)}


# Api to get prompt for all competency questions with their relevant classes
@router.post("/generate_prompt_for_multiple_cq")
def generate_prompt_for_multiple_cq_api(
    graph_path: str, file_path: str, output_path: str, app_state=Depends(get_app_state)
):
    try:
        models = ["bert", "bge", "qwen", "nvidia"]
        logger.info(f"Reading data from {file_path}...")
        file_content = None
        cq_with_relavant_classes = []
        with open(file_path, "r") as f:
            file_content = json.load(f)
            models = (
                file_content["summary"][0]["per_model"].keys()
                if file_content
                and "summary" in file_content
                and len(file_content["summary"]) > 0
                else models
            )
        for data in file_content["summary"]:
            cq_with_relavant_classes.append(
                {
                    "cq": data.get("cq"),
                    "per_model": [
                        {
                            "model": model,
                            "classes": data["per_model"][model]["top_classes"],
                        }
                        for model in models
                    ],
                }
            )
        class_info = {}
        prefix_namespaces = {}
        # Generating prompt for each competency questions
        for each_cq in cq_with_relavant_classes:
            current_cq = each_cq["cq"]
            for model_info in each_cq["per_model"]:
                classes = [
                    {
                        "name": each_class["class"],
                        "annotation": (
                            each_class["annotation"]
                            if "annotation" in each_class
                            else None
                        ),
                    }
                    for each_class in model_info["classes"]
                    if each_class is not None
                ]
                for cls in classes:
                    classes_that_already_has_info = (
                        class_info and class_info.keys() or []
                    )
                    if cls["name"] in classes_that_already_has_info:
                        info = class_info[cls["name"]]
                    else:
                        info = get_all_relavant_info_about_class(
                            cls["name"], graph_path
                        )
                        class_info[cls["name"]] = info
                    cls["info"] = info
                    prefix_namespaces.update(cls["info"]["namespaces"])
                context = generate_sparql_prompt(current_cq, classes, prefix_namespaces)
                model_info["context"] = context
        # Write everything back to the new file
        output_file_path = output_path or os.path.join(DATA_PATH, f"output.json")
        with open(output_file_path, "w") as f:
            json.dump({"summary": cq_with_relavant_classes}, f, indent=4)

        return {
            "status": "OK",
            "message": f"Prompts generated successfully and saved to {output_file_path}!",
        }
    except Exception as e:
        logger.error(
            f"Error occurred while retrieving relevant classes for competency question: {e}"
        )
        return {"status": "ERROR", "message": str(e)}
