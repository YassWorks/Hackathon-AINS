// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Global state
let selectedFiles = [];
let deferredPrompt;

// DOM Elements
const form = document.getElementById("factCheckForm");
const statementInput = document.getElementById("statement");
const fileUpload = document.getElementById("fileUpload");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");
const submitBtn = document.getElementById("submitBtn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const installPrompt = document.getElementById("installPrompt");
const installBtn = document.getElementById("installBtn");

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  setupPWA();
  checkAPIConnection();
});

function setupEventListeners() {
  // Form submission
  form.addEventListener("submit", handleSubmit);

  // File upload
  fileUpload.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileSelect);

  // Drag and drop
  fileUpload.addEventListener("dragover", handleDragOver);
  fileUpload.addEventListener("dragleave", handleDragLeave);
  fileUpload.addEventListener("drop", handleDrop);

  // Install app
  installBtn.addEventListener("click", installApp);
}

function setupPWA() {
  // Register service worker
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => console.log("SW registered:", registration))
      .catch((error) => console.log("SW registration failed:", error));
  }

  // Handle install prompt
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallPrompt();
  });

  // Handle app installed
  window.addEventListener("appinstalled", () => {
    hideInstallPrompt();
    showNotification("App installed successfully! 🎉");
  });
}

function showInstallPrompt() {
  installPrompt.style.display = "block";
}

function hideInstallPrompt() {
  installPrompt.style.display = "none";
}

async function installApp() {
  if (!deferredPrompt) return;

  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;

  if (outcome === "accepted") {
    console.log("User accepted install");
  }

  deferredPrompt = null;
  hideInstallPrompt();
}

async function checkAPIConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      showNotification("✅ Connected to AINS API", "success");
    } else {
      throw new Error("API health check failed");
    }
  } catch (error) {
    console.error("API connection failed:", error);
    showNotification(
      "⚠️ Cannot connect to AINS API. Please check if the backend is running.",
      "warning"
    );
  }
}

function handleDragOver(e) {
  e.preventDefault();
  fileUpload.classList.add("dragover");
}

function handleDragLeave(e) {
  e.preventDefault();
  fileUpload.classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  fileUpload.classList.remove("dragover");

  const files = Array.from(e.dataTransfer.files);
  addFiles(files);
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  addFiles(files);
}

function addFiles(files) {
  const validFiles = files.filter((file) => {
    const isImage = file.type.startsWith("image/");
    const isAudio = file.type.startsWith("audio/");
    return isImage || isAudio;
  });

  selectedFiles = [...selectedFiles, ...validFiles];
  updateFileList();

  if (validFiles.length !== files.length) {
    showNotification(
      "⚠️ Some files were skipped. Only images and audio files are supported.",
      "warning"
    );
  }
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  updateFileList();
}

function updateFileList() {
  if (selectedFiles.length === 0) {
    fileList.innerHTML = "";
    return;
  }

  fileList.innerHTML = selectedFiles
    .map(
      (file, index) => `
        <div class="file-item">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
            <button type="button" class="remove-file" onclick="removeFile(${index})">×</button>
        </div>
    `
    )
    .join("");
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

async function handleSubmit(e) {
  e.preventDefault();

  const statement = statementInput.value.trim();
  if (!statement) {
    showNotification("❌ Please enter a statement to verify.", "error");
    return;
  }

  setLoading(true);
  hideResult();

  try {
    const formData = new FormData();
    formData.append("prompt", statement);

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch(`${API_BASE_URL}/classify`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    displayResult(data);
  } catch (error) {
    console.error("Analysis failed:", error);
    showNotification("❌ Analysis failed. Please try again.", "error");
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  loading.style.display = isLoading ? "block" : "none";
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading
    ? "⏳ Analyzing..."
    : "🔍 Analyze Statement";
}

function hideResult() {
  result.style.display = "none";
}

function displayResult(data) {
  const verdict = document.getElementById("verdict");
  const explanation = document.getElementById("explanation");
  const confidenceValue = document.getElementById("confidenceValue");
  const processingTime = document.getElementById("processingTime");
  const modelsUsed = document.getElementById("modelsUsed");
  const sources = document.getElementById("sources");
  const sourcesList = document.getElementById("sourcesList");

  // Set verdict
  const verdictClass = data.verdict.toLowerCase();
  verdict.className = `verdict ${verdictClass}`;
  verdict.innerHTML = `
        <div>${getVerdictEmoji(data.verdict)} ${data.verdict}</div>
        ${
          data.confidence
            ? `<div class="confidence">${data.confidence}% confidence</div>`
            : ""
        }
    `;

  // Set explanation
  explanation.textContent = data.explanation || "No explanation available.";

  // Set stats
  confidenceValue.textContent = data.confidence ? `${data.confidence}%` : "N/A";
  processingTime.textContent = data.processing_time
    ? `${data.processing_time}s`
    : "N/A";
  modelsUsed.textContent = data.models_used ? data.models_used.length : "0";

  // Set sources
  if (data.sources && data.sources.length > 0) {
    sourcesList.innerHTML = data.sources
      .map(
        (source) => `
            <div class="source-item">${source}</div>
        `
      )
      .join("");
    sources.style.display = "block";
  } else {
    sources.style.display = "none";
  }

  result.style.display = "block";
  result.scrollIntoView({ behavior: "smooth" });
}

function getVerdictEmoji(verdict) {
  switch (verdict.toUpperCase()) {
    case "FACT":
      return "✅";
    case "MYTH":
      return "⚠️";
    case "SCAM":
      return "🚨";
    default:
      return "❓";
  }
}

function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
    `;

  // Set background color based on type
  const colors = {
    success: "#4CAF50",
    warning: "#FF9800",
    error: "#F44336",
    info: "#2196F3",
  };
  notification.style.backgroundColor = colors[type] || colors.info;
  notification.textContent = message;

  // Add to DOM
  document.body.appendChild(notification);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease";
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Make removeFile available globally
window.removeFile = removeFile;
