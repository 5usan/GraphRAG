import re
import torch
import numpy as np
from gensim.models import KeyedVectors
from transformers import BertTokenizer, BertModel

from utils.logger import init_logger
from constants.constants import device

logger = init_logger()


def load_pretrained_word2vec(model_path=None):
    """Load pre-trained Google News word2vec model"""
    try:
        if model_path is None:
            # Try to load from gensim downloader
            model_path = (
                "D:/Study/Masters/Thesis/src/models/GoogleNews-vectors-negative300.bin"
            )

        model = KeyedVectors.load_word2vec_format(model_path, binary=True)
        logger.info(
            f"Pre-trained word2vec model loaded successfully (vector size: {model.vector_size})"
        )
        return model
    except Exception as e:
        logger.error(f"Failed to load word2vec model: {e}")
        return None


def split_words(word):
    """Convert camelCase class names to tokens"""
    # Split camelCase: "EnslaveIndividual" -> ["enslave", "individual"]
    tokens = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", word)
    return [t.lower() for t in tokens if t]


def get_word2vec_embedding(model, word):
    """Get word2vec embedding for a class name"""
    if not model:
        return None

    tokens = split_words(word)
    # Average embeddings of all tokens in the class name
    embeddings = []
    for token in tokens:
        try:
            if token in model:
                embeddings.append(model[token])
        except KeyError:
            # Word not in vocabulary - skip it
            continue

    if embeddings:
        # Return averaged embedding
        return np.mean(embeddings, axis=0).tolist()

    return None


def load_pretrained_bert(model_name="bert-base-uncased"):
    """Load pre-trained BERT model and tokenizer"""
    try:
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)
        model.eval()  # Set model to evaluation mode
        logger.info(f"Pre-trained BERT model loaded successfully ({model_name})")
        return {"model": model, "tokenizer": tokenizer}
    except Exception as e:
        logger.error(f"Failed to load BERT model: {e}")
        return None


def get_bert_embedding(bert_model, word):
    """Get BERT embedding for a class name"""
    if not bert_model:
        return None

    tokenizer = bert_model["tokenizer"]
    model = bert_model["model"]

    # Move model to GPU
    model = model.to(device)

    try:
        tokens = split_words(word)
        if not tokens:
            return None

        # Join tokens with spaces for better BERT tokenization
        input_text = " ".join(tokens)

        # Tokenizer automatically adds [CLS] and [SEP] tokens
        inputs = tokenizer(input_text, return_tensors="pt").to(device)

        # Forward pass through BERT model (no gradient calculation)
        with torch.no_grad():
            outputs = model(**inputs)

        # Get the last hidden states [batch_size, seq_length, 768]
        last_hidden_states = outputs.last_hidden_state

        # Extract [CLS] token embedding (first position)
        cls_embedding = last_hidden_states[0, 0, :].cpu().numpy()
        return cls_embedding.tolist()

    except Exception as e:
        logger.error(f"Failed to generate BERT embedding for '{word}': {e}")
        return None
