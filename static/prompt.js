showdown.extension('only-inline-stuff', function () {
  return [{
    type: 'output',
    filter: function (text) {
      // remove paragraphs
      text = text.replace(/<\/?p[^>]*>/g, '');

      // remove code (if you want)
      // text = text.replace(/<\/?code[^>]*>/g, '');

      //add other stuff here that you want to remove
      // text = text.replace(, '');
      return text;
    }
  }];
});  // To remove paragraph boxes

const converter = new showdown.Converter({ extensions: ['only-inline-stuff'], strikethrough: true, disableForced4SpacesIndentedSublists: true });  // To convert .md from GTP into .html

const promptForm = document.getElementById("prompt-form");
const submitButton = document.getElementById("submit-button");
const importButton = document.getElementById("import-button");
const questionButton = document.getElementById("question-button");
const messagesContainer = document.getElementById("messages-container");

// Fonction pour défiler vers le bas
const scrollToBottom = () => {
  window.scrollTo(0, document.body.scrollHeight);
};

const appendHumanMessage = (message) => {
  const humanMessageElement = document.createElement("div");
  humanMessageElement.classList.add("message", "message-human");
  humanMessageElement.innerHTML = converter.makeHtml(message);
  messagesContainer.appendChild(humanMessageElement);
};

const appendAIMessage = async (messagePromise) => {
  // Add a loader to the interface
  const loaderElement = document.createElement("div");
  loaderElement.classList.add("message");
  loaderElement.innerHTML =
    "<div class='loader'><div></div><div></div><div></div>";
  messagesContainer.appendChild(loaderElement);
  scrollToBottom();  // Faire défiler automatiquement

  // Await the answer from the server
  const messageToAppend = await messagePromise();

  // Replace the loader with the answer
  loaderElement.classList.remove("loader");
  loaderElement.innerHTML = messageToAppend;

  scrollToBottom();  // Faire défiler automatiquement
};

const handlePrompt = async (event) => {
  event.preventDefault();
  // Parse form data in a structured object
  const data = new FormData(event.target);
  promptForm.reset();

  let url = "/prompt";
  if (questionButton.dataset.question !== undefined) {
    url = "/answer";
    data.append("question", questionButton.dataset.question);
    delete questionButton.dataset.question;
    questionButton.classList.remove("hidden");
    submitButton.innerHTML = "Envoyer";
  }

  appendHumanMessage(data.get("prompt"));

  await appendAIMessage(async () => {
    const response = await fetch(url, {
      method: "POST",
      body: data,
    });
    const result = await response.json();
    return converter.makeHtml(result.answer);  // .md -> .html for prompt
  });
};

promptForm.addEventListener("submit", handlePrompt);

const handleQuestionClick = async (event) => {
  appendAIMessage(async () => {
    const response = await fetch("/question", {
      method: "GET",
    });
    const result = await response.json();
    const question = converter.makeHtml(result.answer);  // md. -> .html for question

    questionButton.dataset.question = question;
    questionButton.classList.add("hidden");
    submitButton.innerHTML = "Répondre à la question";
    return question;
  });
};

questionButton.addEventListener("click", handleQuestionClick);

//Mode sombre 

// Fonction pour basculer le mode sombre
function toggleDarkMode() {
  const body = document.body;
  const button = document.getElementById('toggle-mode');

  if (body.classList.contains('light-mode')) {
    // Basculer vers le mode sombre
    body.classList.remove('light-mode');
    body.classList.add('dark-mode');
    button.innerHTML = "☀️";

  } else {
    // Basculer vers le mode clair
    body.classList.remove('dark-mode');
    body.classList.add('light-mode');
    button.innerHTML = "🌙";
  }
}

// Ajouter un écouteur d'événement au bouton
document.getElementById('toggle-mode').addEventListener('click', toggleDarkMode);

// Optionnel : Vérifier le mode préféré de l'utilisateur au chargement de la page
function checkPreferredColorScheme() {
  const body = document.body;
  const button = document.getElementById('toggle-mode');

  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // Basculer vers le mode sombre
    body.classList.remove('light-mode');
    body.classList.add('dark-mode');
    button.innerHTML = "☀️";
  } else {
    // Basculer vers le mode clair
    body.classList.remove('dark-mode');
    body.classList.add('light-mode');
    button.innerHTML = "🌙";
  }
}

// Appeler cette fonction au chargement de la page
window.addEventListener('load', checkPreferredColorScheme);

const handleImportClick = () => {
  // Create an input element dynamically
  const inputElement = document.createElement("input");
  inputElement.type = "file";
  inputElement.accept = ".pdf, .txt, .html, .md, .docx"; // Accepter PDF, TXT, HTML MD et DOCX

  // Trigger the file selection dialog
  inputElement.click();

  // Listen for file selection
  inputElement.addEventListener("change", async () => {
    const file = inputElement.files[0];
    if (file) {
      // Create a FormData object and append the selected file
      const formData = new FormData();
      formData.append("file", file);

      try {
        // Send the file to the API
        const response = await fetch("/file", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          appendAIMessage(() => Promise.resolve(`Fichier ajouté avec succès : ${result.response}`));
        } else {
          appendAIMessage(() => Promise.resolve("Impossible de télécharger le fichier !"));
        }
      } catch (error) {
        appendAIMessage(() => Promise.resolve("Le téléchargement du fichier a échoué"));
      }
    }
  });
}

importButton.addEventListener("click", handleImportClick);
