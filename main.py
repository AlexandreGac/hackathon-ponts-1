import os

from flask import Flask
from flask import render_template
from flask import request

from docx import Document

from src.utils.ask_question_to_pdf import (
    ask_question_to_pdf,
    initialize_session,
    read_pdf,
)

app = Flask(__name__)


@app.route("/")
def hello_world(name=None):
    return render_template("index.html", name=name)


@app.route("/prompt", methods=["POST"])
def prompt():
    question = request.form["prompt"]
    answer = ask_question_to_pdf(question)
    return {"answer": answer}


@app.route("/question", methods=["GET"])
def question():
    answer = ask_question_to_pdf("Pose-moi une question sur le texte.")
    return {"answer": answer}


@app.route("/answer", methods=["POST"])
def response():
    answer = request.form["prompt"]
    gpt_answer = ask_question_to_pdf(answer)
    return {"answer": gpt_answer}


@app.route("/file", methods=["POST"])
def upload_file():
    # Vérification si le fichier a bien été envoyé avec la requête
    if "file" not in request.files:
        return {"error": "No file part"}, 400

    file = request.files["file"]

    # Vérification si un fichier a été sélectionné
    if file.filename == "" or not file:
        return {"error": "No selected file"}, 400

    # Si c'est un fichier PDF
    if file.filename.endswith(".pdf"):
        file_path = "document.pdf"
        file.save(file_path)
        filename = os.path.join(os.path.dirname(__file__), "document.pdf")
        context = read_pdf(filename)
        initialize_session(context)
        return {"response": file.filename}

    # Si c'est un fichier TXT
    elif file.filename.endswith(".txt"):
        file_path = "document.txt"
        file.save(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        initialize_session(content)
        return {"response": file.filename}

    # Si c'est un fichier HTML
    elif file.filename.endswith(".html"):
        file_path = "document.html"
        file.save(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        initialize_session(
            content
        )  # Traiter le contenu HTML comme du texte brut ou autre
        return {"response": file.filename}

    # Si c'est un fichier Markdown (MD)
    elif file.filename.endswith(".md"):
        file_path = "document.md"
        file.save(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        initialize_session(content)  # Markdown traité comme du texte brut
        return {"response": file.filename}

    # Si c'est un fichier DOCX (Word)
    elif file.filename.endswith(".docx"):
        file_path = "document.docx"
        file.save(file_path)
        document = Document(file_path)
        docx_text = "\n".join(
            [para.text for para in document.paragraphs]
        )  # Extraction du texte
        initialize_session(docx_text)
        return {"response": file.filename}

    # Si le fichier n'est pas pris en charge
    return {
        "error": "Invalid file type. Only PDFs, TXT, HTML, and MD are allowed."
    }, 400
