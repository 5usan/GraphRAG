import os
import torch
from dotenv import load_dotenv

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

GRAPH_PATH = os.path.join(os.getcwd(), "datasets", "schema")
DATA_PATH = os.path.join(os.getcwd(), "datasets", "data")

PREPOSITIONS = [
    "in",
    "on",
    "at",
    "by",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "of",
    "up",
    "down",
    "over",
    "under",
]
ARTICLES = ["a", "an", "the"]
WH_QUESTIONS = [
    "what",
    "which",
    "who",
    "whom",
    "whose",
    "where",
    "when",
    "why",
    "how",
]
VERBS = [
    "is",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
]
CONJUNCTIONS = [
    "and",
    "but",
    "or",
    "nor",
    "for",
    "yet",
    "so",
    "because",
    "although",
    "since",
    "unless",
    "while",
    "whereas",
    "after",
    "before",
    "once",
    "until",
    "when",
    "whenever",
    "if",
    "provided that",
    "as long as",
    "in case",
]
