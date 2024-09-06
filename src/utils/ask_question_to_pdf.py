from io import StringIO
import os
import fitz
import openai
from openai import OpenAI
from dotenv import load_dotenv
from nltk.tokenize import sent_tokenize

load_dotenv()


def open_file(filepath):
    with open(filepath, "r", encoding="utf-8") as infile:
        return infile.read()


openai.api_key = os.getenv("OPENAI_API_KEY")


def read_pdf(filename):
    context = ""

    # Open the PDF file
    with fitz.open(filename) as pdf_file:
        # Get the number of pages in the PDF file
        num_pages = pdf_file.page_count

        # Loop through each page in the PDF file
        for page_num in range(num_pages):
            # Get the current page
            page = pdf_file[page_num]

            # Get the text from the current page
            page_text = page.get_text().replace("\n", "")

            # Append the text to context
            context += page_text
    return context


def split_text(text, chunk_size=5000):
    chunks = []
    current_chunk = StringIO()
    current_size = 0
    sentences = sent_tokenize(text)
    for sentence in sentences:
        sentence_size = len(sentence)
        if sentence_size > chunk_size:
            while sentence_size > chunk_size:
                chunk = sentence[:chunk_size]
                chunks.append(chunk)
                sentence = sentence[chunk_size:]
                sentence_size -= chunk_size
                current_chunk = StringIO()
                current_size = 0
        if current_size + sentence_size < chunk_size:
            current_chunk.write(sentence)
            current_size += sentence_size
        else:
            chunks.append(current_chunk.getvalue())
            current_chunk = StringIO()
            current_chunk.write(sentence)
            current_size = sentence_size
    if current_chunk:
        chunks.append(current_chunk.getvalue())
    return chunks


filename = os.path.join(os.path.dirname(__file__), "../../filename.pdf")
document = read_pdf(filename)
chunks = split_text(document)

client = OpenAI()

discussion = [
    {
        "role": "system",
        "content": "Tu es un assistant nommé Étud qui aide à comprendre le contenu d'une certaine "
        "documentation. Voici la documentation à laquelle tu as accès et pour "
        "laquelle tu dois aider : " + document,
    }
]


def ask_question_to_pdf(request):
    discussion.append({"role": "user", "content": request})
    response = client.chat.completions.create(model="gpt-4o-mini", messages=discussion)
    message = response.choices[0].message.content
    discussion.append({"role": "assistant", "content": message})
    return message


def initialize_session(context):
    global document
    document = context
    discussion.clear()
    discussion.append(
        {
            "role": "system",
            "content": "Tu es un assistant nommé Étud"
            "qui aide à comprendre le contenu d'une certaine documentation. "
            "Voici la documentation à laquelle tu as accès et pour laquelle"
            "tu dois aider : " + document,
        }
    )
