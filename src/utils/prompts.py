from utils.logger import init_logger

logger = init_logger()

def generate_sparql_prompt(competency_question: str, relavent_classes: list):
    classes_section = ""
    for cls in relavent_classes:
        required, optional = parse_owl_properties(cls["info"]["properties"])
        sub_class_of = cls["info"].get("sub_class_of", [])
        sub_classes = cls["info"].get("sub_classes", [])
        classes_section += f"""
Class: {cls['name'][0] if isinstance(cls['name'], list) else cls['name']}
Parent Classes: {', '.join(sub_class_of) if sub_class_of else 'None'}
Sub Classes: {', '.join(sub_classes) if sub_classes else 'None'}

Required properties:
{format_properties(required)}

Optional properties:
{format_properties(optional)}
            """
        prompt = f"""
## Task Description:

You are a Semantic Web expert. Your goal is to convert the following natural language question into a technically accurate SPARQL query based on the provided ontology schema.

## Instructions:

1. Think Step-by-Step: First, analyze the natural language query. Identify the key entities, properties, and relationships required.
2. Draft the Logic: Write out the triple patterns and filters needed in plain English.
3. Generate SPARQL: Finally, provide the formal SPARQL query.

## Ontology Schema Information with relevant classes and their properties:
{classes_section}

## Competency Question:

{competency_question}

## Output Format:

Provide your response in natural language text. Use the following headers:
# Reasoning
# SPARQL Query
        """
    return prompt


def parse_owl_properties(properties: list) -> tuple:
    """Parse OWL restrictions and return (required, optional) properties"""
    required = []
    optional = []

    for prop in properties:
        prop_name = prop.get("owl#onProperty", "Unknown")
        prop_type = None
        cardinality = "N/A"

        # Determine type and cardinality
        if "owl#onClass" in prop:
            prop_type = prop["owl#onClass"]
        elif "owl#onDataRange" in prop:
            prop_type = prop["owl#onDataRange"]
        elif "owl#someValuesFrom" in prop:
            prop_type = prop["owl#someValuesFrom"]
            cardinality = "some values"
        elif "owl#allValuesFrom" in prop:
            prop_type = prop["owl#allValuesFrom"]
            cardinality = "all values"

        # Determine if required or optional based on cardinality
        min_card = int(prop.get("owl#minQualifiedCardinality", 0))
        qual_card = prop.get("owl#qualifiedCardinality")

        if min_card >= 1 or qual_card:  # Required
            if qual_card:
                cardinality = f"exactly {qual_card}"
            elif min_card >= 1:
                cardinality = f"minimum {min_card}"
            required.append(
                {"name": prop_name, "type": prop_type, "cardinality": cardinality}
            )
        else:  # Optional
            cardinality = f"minimum {min_card}"
            optional.append(
                {"name": prop_name, "type": prop_type, "cardinality": cardinality}
            )

    return required, optional


def format_properties(properties: list) -> str:
    if not properties:
        return "  None"
    return "\n".join(
        [f"  - {p['name']}: {p['cardinality']}, type {p['type']}" for p in properties]
    )
