import pandas as pd
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Retrieve API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Dictionary to store translated entries
translation_dict = {}


def translate_text(text, target_language="en"):
    if pd.isna(text) or text.strip() == "":
        return text  # Return as is if the cell is empty or NaN

    if text in translation_dict:
        return translation_dict[text]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a translator. Translate the user-provided text to {target_language} "
                    'but leave any text between double quotes ("...") unchanged. Do not include any explanations or comments.'
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        max_completion_tokens=2000,
        temperature=0.3,
    )

    translated_text = response.choices[0].message.content.strip()
    translation_dict[text] = translated_text  # Store the translation
    return translated_text


def standardize_product_format(text):
    # Simple example of standardizing format
    if pd.isna(text) or text.strip() == "":
        return text  # Return as is if the cell is empty or NaN

    if "Embroidery" in text and "T-Shirt" in text:
        try:
            parts = text.split("With")
            base = parts[0].strip()
            details = parts[1].strip()
            standardized = f"{base} with {details}"
            return standardized
        except IndexError:
            return text
    return text


def translate_csv(
    input_file, output_file, column_names_to_translate, target_language="en"
):
    df = pd.read_csv(input_file)

    logger.info("Reading header row...")
    columns_to_translate = [column_name for column_name in column_names_to_translate]
    logger.info(f"Columns to translate: {columns_to_translate}")

    for column in columns_to_translate:
        logger.info(f"Translating column {column}...")
        df[column] = df[column].apply(standardize_product_format)
        df[column] = df[column].apply(
            lambda cell: translate_text(cell, target_language)
        )

    df.to_csv(output_file, index=False)
    logger.info("Translation process completed.")


# Ensure the 'data' folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Example usage
input_csv_path = os.path.join("data", "input.csv")
output_csv_path = os.path.join("data", "output.csv")

column_names_to_translate = [
    "Nome",
    "Breve descrizione",
    "Meta: misure_prodotto",
    "Meta: composizione",
]

logger.info("Starting translation process...")
translate_csv(
    input_csv_path, output_csv_path, column_names_to_translate, target_language="en"
)
logger.info("Translation process completed.")
