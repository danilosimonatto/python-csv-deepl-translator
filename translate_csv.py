import csv
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


def translate_text(text, target_language="en"):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that translates text to {target_language}.",
            },
            {
                "role": "user",
                "content": f"Translate the following text to {target_language}: {text}",
            },
        ],
        max_tokens=2000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def translate_csv(
    input_file, output_file, column_names_to_translate, target_language="en"
):
    with open(input_file, mode="r", encoding="utf-8") as infile, open(
        output_file, mode="w", encoding="utf-8", newline=""
    ) as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        logger.info("Reading header row...")
        # Read the header row and write it to the output file
        headers = next(reader)
        writer.writerow(headers)

        # Get the indices of the columns to translate
        columns_to_translate = [
            headers.index(column_name) for column_name in column_names_to_translate
        ]
        logger.info(f"Columns to translate: {columns_to_translate}")

        # Translate the specified columns
        for row_num, row in enumerate(reader, start=1):
            logger.info(f"Translating row {row_num}...")
            translated_row = [
                (
                    translate_text(cell, target_language)
                    if index in columns_to_translate
                    else cell
                )
                for index, cell in enumerate(row)
            ]
            writer.writerow(translated_row)
            logger.info(f"Translated row {row_num} completed.")


# Ensure the 'data' folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Example usage
input_csv_path = os.path.join("data", "input.csv")
output_csv_path = os.path.join("data", "output.csv")

# Specify the column names you want to translate
column_names_to_translate = [
    "Name",
    "Short description",
    "Meta: misure_prodotto",
    "Meta: misure_modello",
    "Meta: composizione",
]

logger.info("Starting translation process...")
translate_csv(
    input_csv_path, output_csv_path, column_names_to_translate, target_language="en"
)
logger.info("Translation process completed.")
