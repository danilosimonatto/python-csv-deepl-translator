import pandas as pd
import requests

from dotenv import load_dotenv
import os

load_dotenv()

# Replace 'DEEPL_API_KEY' with your actual API key
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


def translate_text(text, target_lang="EN"):
    if not text:
        return ""
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang,
    }
    response = requests.get(DEEPL_API_URL, params=params)
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return text


def translate_csv(input_csv, output_csv, columns_to_translate, target_lang):
    df = pd.read_csv(input_csv)
    for column in columns_to_translate:
        df[column] = df[column].apply(translate_text, target_lang=target_lang)
    df.to_csv(output_csv, index=False)
    print(f"Translation completed. Translated file saved as {output_csv}")


if __name__ == "__main__":
    input_csv = "input.csv"
    output_csv = "translated.csv"
    columns_to_translate = [
        "Name",
        "Short description",
        "Meta: misure_prodotto",
    ]  # columns you want to translate
    target_lang = "EN"  # target language code

    translate_csv(input_csv, output_csv, columns_to_translate, target_lang)
