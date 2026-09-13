const API_URL = "";
const MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024;

const pdfInput = document.getElementById("pdfInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const uploadDropzone = document.getElementById("uploadDropzone");
const selectedFile = document.getElementById("selectedFile");
const documentName = document.getElementById("documentName");
const documentMeta = document.getElementById("documentMeta");
const currentDocumentCard = document.getElementById("currentDocumentCard");
const resetDocumentButton = document.getElementById("resetDocumentButton");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const chatHint = document.getElementById("chatHint");
const groundedStatus = document.getElementById("groundedStatus");
const groundedStatusText = document.getElementById("groundedStatusText");
const welcomeUploadButton = document.getElementById("welcomeUploadButton");

let currentDocument = null;
let currentDocumentId = null;
let selectedPdf = null;
let welcomeHTML = "";
let processingStatusTimer = null;

if (chatMessages) {
    welcomeHTML = chatMessages.innerHTML;
}


function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + " B";
    }

    if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(1) + " KB";
    }

    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}


function setUploadStatus(message, state) {
    if (!uploadStatus) {
        return;
    }

    uploadStatus.textContent = message;
    uploadStatus.classList.remove("is-success", "is-error", "is-busy");

    if (state) {
        uploadStatus.classList.add(state);
    }
}


function setChatHint(message) {
    if (chatHint) {
        chatHint.textContent = message || "";
    }
}


function setChatEnabled(enabled) {
    if (questionInput) {
        questionInput.disabled = !enabled;
    }

    if (sendButton) {
        sendButton.disabled = !enabled;
    }
}


function setDocumentReady(isReady) {
    if (currentDocumentCard) {
        currentDocumentCard.classList.toggle("empty", !isReady);
    }

    if (resetDocumentButton) {
        resetDocumentButton.hidden = !isReady;
    }

    if (groundedStatus) {
        groundedStatus.classList.toggle("inactive", !isReady);
    }

    if (groundedStatusText) {
        groundedStatusText.textContent = isReady
            ? "Document Grounded"
            : "No document loaded";
    }

    setChatEnabled(isReady);
}


function showSelectedFile(file) {
    if (!selectedFile) {
        return;
    }

    if (!file) {
        selectedFile.textContent = "";
        selectedFile.classList.remove("is-visible");
        return;
    }

    selectedFile.textContent =
        file.name + " · " + formatFileSize(file.size);
    selectedFile.classList.add("is-visible");
}


function isPdfFile(file) {
    if (!file) {
        return false;
    }

    return (
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf")
    );
}


function validateSelectedFile(file) {
    if (!file) {
        return "Please select a PDF first.";
    }

    if (!isPdfFile(file)) {
        return "Only PDF files are allowed.";
    }

    if (file.size > MAX_PDF_SIZE_BYTES) {
        return "This file is larger than 10 MB. Please choose a smaller PDF.";
    }

    return "";
}


function friendlyUploadMessage(status, data) {
    const detail = typeof data?.detail === "string" ? data.detail : "";

    if (status === 413 || detail.includes("too large")) {
        return "This file is larger than 10 MB. Please choose a smaller PDF.";
    }

    if (detail.includes("Only PDF")) {
        return "Only PDF files are allowed.";
    }

    if (
        detail.includes("extract") ||
        detail.includes("readable text") ||
        detail.includes("chunks")
    ) {
        return "The document could not be processed. Please try another PDF.";
    }

    if (status >= 500) {
        return "Upload failed. Please try again.";
    }

    return "Upload failed. Please try another PDF.";
}


function friendlyChatMessage(status, data) {
    const detail = typeof data?.detail === "string" ? data.detail : "";

    if (status === 404) {
        return "I couldn't find relevant information in the uploaded document.";
    }

    if (detail && !detail.includes("Error") && !detail.includes("Traceback")) {
        return detail;
    }

    return "I couldn't answer that right now. Please try again.";
}


async function readResponse(response) {
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        try {
            return await response.json();
        } catch (error) {
            return {};
        }
    }

    try {
        const text = await response.text();
        return { detail: text };
    } catch (error) {
        return {};
    }
}


function openFilePicker() {
    if (pdfInput) {
        pdfInput.click();
    }
}


function handleFileChoice(file) {
    if (uploadDropzone) {
        uploadDropzone.classList.remove("has-error", "is-dragover");
    }

    const error = validateSelectedFile(file);

    if (error) {
        selectedPdf = null;
        showSelectedFile(null);

        if (pdfInput) {
            pdfInput.value = "";
        }

        if (uploadDropzone) {
            uploadDropzone.classList.add("has-error");
        }

        setUploadStatus(error, "is-error");
        return;
    }

    selectedPdf = file;
    showSelectedFile(file);
    setUploadStatus("File selected. Click Upload Document to continue.", "");
}


if (uploadDropzone) {
    uploadDropzone.addEventListener("click", openFilePicker);

    uploadDropzone.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openFilePicker();
        }
    });

    uploadDropzone.addEventListener("dragover", function (event) {
        event.preventDefault();
        uploadDropzone.classList.add("is-dragover");
    });

    uploadDropzone.addEventListener("dragleave", function () {
        uploadDropzone.classList.remove("is-dragover");
    });

    uploadDropzone.addEventListener("drop", function (event) {
        event.preventDefault();
        uploadDropzone.classList.remove("is-dragover");

        const file = event.dataTransfer.files[0];
        handleFileChoice(file);
    });
}

if (welcomeUploadButton) {
    welcomeUploadButton.addEventListener("click", openFilePicker);
}

if (pdfInput) {
    pdfInput.addEventListener("change", function () {
        handleFileChoice(pdfInput.files[0]);
    });
}

if (uploadButton) {
    uploadButton.addEventListener("click", uploadDocument);
}

if (resetDocumentButton) {
    resetDocumentButton.addEventListener("click", resetDocument);
}

if (sendButton) {
    sendButton.addEventListener("click", sendMessage);
}

if (questionInput) {
    questionInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
}

document.querySelectorAll("[data-suggestion]").forEach(function (button) {
    button.addEventListener("click", function () {
        useSuggestion(button.getAttribute("data-suggestion"));
    });
});


async function uploadDocument() {
    const file = selectedPdf || (pdfInput && pdfInput.files[0]);
    const validationError = validateSelectedFile(file);

    if (validationError) {
        setUploadStatus(validationError, "is-error");
        setChatHint(validationError);
        return;
    }

    uploadButton.disabled = true;
    setChatEnabled(false);
    setUploadStatus("Uploading...", "is-busy");

    processingStatusTimer = window.setTimeout(function () {
        setUploadStatus("Processing document...", "is-busy");
    }, 400);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await readResponse(response);

        if (!response.ok) {
            throw {
                friendly: friendlyUploadMessage(response.status, data)
            };
        }

        currentDocument = data.filename;
        currentDocumentId = data.document_id;

        if (documentName) {
            documentName.textContent = data.filename;
        }

        if (documentMeta) {
            documentMeta.textContent =
                data.pages + " pages · " +
                data.characters + " characters · " +
                data.chunks + " chunks";
        }

        setUploadStatus("Document ready.", "is-success");
        setChatHint("");
        setDocumentReady(true);
        clearChat();
        addAIMessage(
            "Document uploaded successfully.\n\n" +
            "I am ready to answer questions about \"" +
            data.filename +
            "\"."
        );

        if (questionInput) {
            questionInput.focus();
        }
    } catch (error) {
        console.error("UPLOAD ERROR:", error);

        currentDocument = null;
        currentDocumentId = null;
        setDocumentReady(false);

        const message = error && error.friendly
            ? error.friendly
            : "Upload failed. Please try again.";

        setUploadStatus(message, "is-error");
        setChatHint(message);
    } finally {
        if (processingStatusTimer) {
            window.clearTimeout(processingStatusTimer);
            processingStatusTimer = null;
        }

        uploadButton.disabled = false;
        uploadButton.textContent = "Upload Document";
    }
}


function resetDocument() {
    currentDocument = null;
    currentDocumentId = null;
    selectedPdf = null;

    if (pdfInput) {
        pdfInput.value = "";
    }

    showSelectedFile(null);

    if (documentName) {
        documentName.textContent = "No document uploaded";
    }

    if (documentMeta) {
        documentMeta.textContent = "Upload a PDF to start";
    }

    if (uploadDropzone) {
        uploadDropzone.classList.remove("has-error", "is-dragover");
    }

    setUploadStatus("Select a PDF to begin.", "");
    setChatHint("");
    setDocumentReady(false);
    restoreWelcome();
}


async function sendMessage() {
    const question = questionInput ? questionInput.value.trim() : "";

    if (!question) {
        setChatHint("Please enter a question before sending.");
        return;
    }

    if (!currentDocumentId) {
        setChatHint("Upload a PDF before asking a question.");
        return;
    }

    setChatHint("");
    addUserMessage(question);
    questionInput.value = "";
    setChatEnabled(false);

    const loadingMessage = addLoadingMessage();

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                document_id: currentDocumentId
            })
        });

        const data = await readResponse(response);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        if (!response.ok) {
            throw {
                friendly: friendlyChatMessage(response.status, data)
            };
        }

        if (!data.answer || typeof data.answer !== "string") {
            throw {
                friendly: "I couldn't answer that right now. Please try again."
            };
        }

        addAIMessage(data.answer, data.sources || []);
    } catch (error) {
        console.error("CHAT ERROR:", error);

        if (loadingMessage) {
            loadingMessage.remove();
        }

        const message = error && error.friendly
            ? error.friendly
            : "I couldn't answer that right now. Please try again.";

        addAIMessage(message);
    } finally {
        setChatEnabled(true);

        if (questionInput) {
            questionInput.focus();
        }
    }
}


function addUserMessage(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message user";

    const stack = document.createElement("div");
    stack.className = "message-stack";

    const role = document.createElement("div");
    role.className = "message-role";
    role.textContent = "You";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message;

    stack.appendChild(role);
    stack.appendChild(content);
    messageDiv.appendChild(stack);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}


function addAIMessage(message, sources) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message ai";

    const stack = document.createElement("div");
    stack.className = "message-stack";

    const role = document.createElement("div");
    role.className = "message-role";
    role.textContent = "CERTUS AI";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = typeof message === "string"
        ? message
        : "I couldn't answer that right now. Please try again.";

    if (Array.isArray(sources) && sources.length > 0) {
        const sourceDiv = document.createElement("div");
        sourceDiv.className = "sources";

        const title = document.createElement("div");
        title.className = "sources-title";
        title.textContent = "Sources";
        sourceDiv.appendChild(title);

        sources.forEach(function (source) {
            const documentTitle = source.document || currentDocument || "Document";
            const chunk = source.chunk;
            const line = document.createElement("div");
            line.className = "source-chip";
            line.textContent = chunk
                ? "📄 " + documentTitle + " · Chunk " + chunk
                : "📄 " + documentTitle;
            sourceDiv.appendChild(line);
        });

        content.appendChild(sourceDiv);
    }

    stack.appendChild(role);
    stack.appendChild(content);
    messageDiv.appendChild(stack);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}


function addLoadingMessage() {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message ai";

    const stack = document.createElement("div");
    stack.className = "message-stack";

    const role = document.createElement("div");
    role.className = "message-role";
    role.textContent = "CERTUS AI";

    const content = document.createElement("div");
    content.className = "message-content";

    const thinking = document.createElement("div");
    thinking.className = "thinking";

    const label = document.createElement("span");
    label.textContent = "CERTUS AI is thinking...";

    const loading = document.createElement("div");
    loading.className = "loading";
    loading.setAttribute("aria-hidden", "true");
    loading.innerHTML = "<span></span><span></span><span></span>";

    thinking.appendChild(label);
    thinking.appendChild(loading);
    content.appendChild(thinking);
    stack.appendChild(role);
    stack.appendChild(content);
    messageDiv.appendChild(stack);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}


function useSuggestion(question) {
    if (!currentDocumentId) {
        setChatHint("Upload a PDF before asking a question.");
        return;
    }

    if (!questionInput) {
        return;
    }

    questionInput.value = question;
    questionInput.focus();
    sendMessage();
}


function clearChat() {
    if (!chatMessages) {
        return;
    }

    chatMessages.innerHTML = "";
}


function restoreWelcome() {
    if (!chatMessages) {
        return;
    }

    chatMessages.innerHTML = welcomeHTML;

    const restoredUpload = document.getElementById("welcomeUploadButton");

    if (restoredUpload) {
        restoredUpload.addEventListener("click", openFilePicker);
    }

    document.querySelectorAll("[data-suggestion]").forEach(function (button) {
        button.addEventListener("click", function () {
            useSuggestion(button.getAttribute("data-suggestion"));
        });
    });
}


function scrollToBottom() {
    if (!chatMessages) {
        return;
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


setDocumentReady(false);
setUploadStatus("Select a PDF to begin.", "");
