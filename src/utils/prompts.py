from utils.logger import init_logger

logger = init_logger()

def generate_sparql_prompt(competency_question: str, relavent_classes: list):
    """
    Generate a prompt for the LLM to generate a SPARQL query based on the competency question and relevant classes.
    """
    try:
        prompt = """You are a SPARQL query expert. Your task is to convert a competency question into a SPARQL query based on the provided ontology schema.

        ## Instructions:

        1. Analyze the competency question to identify:
        - Key entities/concepts mentioned
        - Relationships between entities
        - Filters or constraints (time periods, locations, values)
        - What data should be returned

        2. Use the provided ontology context to:
        - Map concepts to classes
        - Identify relevant properties and their constraints
        - Understand cardinality and value restrictions
        - Follow the object property relationships

        3. Generate a SPARQL query that:
        - Uses appropriate prefixes for the enslaved ontology
        - Follows the class and property definitions provided
        - Applies all filters and constraints from the question
        - Returns the relevant results

        4. Structure the query as:
        - PREFIX declarations
        - SELECT clause (what to return)
        - WHERE clause (graph patterns matching the ontology)
        - FILTER clauses (for constraints like date ranges, text searches)
        - OPTIONAL clauses (for non-required properties)

        ## Input Format:
        - Competency Question: {competency_question}
        - Relevant Classes and Properties: [provided ontology context]

        ## Output:
        - SPARQL query only
        - Ensure all property names match ontology exactly
        - Use proper RDF/OWL notation
        - Include comments explaining the query logic

        Competency Question: {competency_question}

        Relevant Classes and Properties:
        """.format(competency_question=competency_question)

        for cls in relavent_classes:
            prompt += f"\n\nClass: {cls['name']}\nProperties: {cls['info']}"

        prompt += "\n\nGenerate the SPARQL query now:"
        return prompt
    except Exception as e:
        logger.error(f"Error occurred while generating SPARQL prompt: {e}")
        return None  