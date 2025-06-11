# 🛡️ MYTH CHASER

**Anti-scam and myth-busting utility powered by AI**

MYTH CHASER is an advanced AI-powered fact-checking and anti-scam detection system that helps users verify the authenticity of claims, statements, and media content. Using multiple machine learning models and real-time web search capabilities, it provides comprehensive analysis to identify facts, myths, and potential scams.

## ✨ Features

### 🤖 Multi-Model AI Analysis
- **Natural Language Inference (NLI)**: RoBERTa-based model for logical reasoning between claims and evidence
- **Sentence-BERT (SBERT)**: Semantic similarity analysis using sentence embeddings
- **ClaimBuster Integration**: Professional fact-checking API for claim verification
- **Google Fact Check API**: Access to Google's comprehensive fact-checking database
- **Fake News Detection**: Specialized model for identifying misinformation patterns
- **AI Explanation Generator**: Microsoft Phi-2 model for detailed explanations

### 🔍 Multi-Format Content Analysis
- **Text Processing**: Direct text input analysis and verification
- **Image Analysis**: OCR text extraction and visual content description using BLIP
- **Audio Processing**: Speech-to-text conversion for audio content verification
- **Drag & Drop Interface**: Seamless file upload with support for multiple formats

### 🌐 Real-Time Web Search
- **DuckDuckGo Integration**: Automated web search for evidence gathering
- **Source Aggregation**: Intelligent collection and processing of relevant information
- **Evidence Synthesis**: Combines multiple sources for comprehensive analysis

### 🎯 Three-Tier Classification System
- **FACT**: Verified true statements with supporting evidence
- **MYTH**: Partially true or misleading information requiring clarification
- **SCAM**: False, harmful, or deceptive content

### 💡 Advanced Voting Algorithm
- Combines predictions from all AI models using weighted consensus
- Handles uncertain predictions gracefully
- Provides confidence-based final verdicts

## 🏗️ Architecture

### Backend (FastAPI)
- **Multi-threaded Processing**: Parallel execution of AI models for faster analysis
- **RESTful API**: Clean `/classify` endpoint for content verification
- **CORS Support**: Seamless frontend-backend communication
- **Error Handling**: Robust error management and graceful degradation

### Frontend (Next.js 15)
- **Modern React Architecture**: Built with React 19 and Next.js 15
- **TypeScript Support**: Full type safety throughout the application
- **Tailwind CSS**: Responsive, modern UI design
- **Real-time Feedback**: Loading states and progress indicators
- **File Management**: Advanced file upload with preview and management

### Machine Learning Models
- **Transformer-based**: State-of-the-art NLP models for text analysis
- **Computer Vision**: BLIP model for image understanding
- **Speech Recognition**: Google Speech Recognition for audio processing
- **Ensemble Methods**: Multiple model predictions combined for accuracy

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PyTorch**: Deep learning framework for AI models
- **Transformers**: Hugging Face transformers library
- **SpeechRecognition**: Audio processing capabilities
- **PIL/Pytesseract**: Image processing and OCR
- **DuckDuckGo Search**: Web search integration

### Frontend
- **Next.js 15**: React-based web framework
- **React 19**: Latest React with concurrent features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Hooks**: Reusable state management logic

### AI Models
- **ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli**: NLI classification
- **all-MiniLM-L6-v2**: Sentence embeddings
- **winterForestStump/Roberta-fake-news-detector**: Fake news detection
- **Salesforce/blip-image-captioning-base**: Image captioning
- **microsoft/phi-2**: Text generation and explanation

## 📁 Project Structure

```
Hack-AINS/
├── apis/                     # Backend API server
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # AI model implementations
│   │   ├── NLI/             # Natural Language Inference
│   │   ├── SBERT/           # Sentence-BERT similarity
│   │   ├── ClaimBuster/     # ClaimBuster API integration
│   │   ├── Google/          # Google Fact Check API
│   │   ├── FakeNewsDetector/# Fake news classification
│   │   └── Explainer/       # AI explanation generation
│   ├── converters/          # Media-to-text conversion utilities
│   ├── web_searcher/        # Web search and evidence gathering
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # Next.js web application
│   ├── app/                 # Next.js app directory
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   └── package.json         # Node.js dependencies
│
└── compose.yaml             # Docker composition (future deployment)
```

## 🚀 Key Capabilities

- **Real-time Analysis**: Process and verify content within seconds
- **Multi-modal Support**: Handle text, images, and audio files seamlessly  
- **Source Verification**: Cross-reference claims with multiple authoritative sources
- **Confidence Scoring**: Provide reliability indicators for all predictions
- **Batch Processing**: Handle multiple files simultaneously
- **Responsive Design**: Works across desktop and mobile devices
- **Privacy-focused**: No data retention, immediate processing and disposal

## 🎨 User Interface

- **Retro Gaming Aesthetic**: Pixel-perfect design with nostalgic appeal
- **Drag & Drop**: Intuitive file upload with visual feedback
- **Real-time Feedback**: Loading animations and progress indicators
- **Color-coded Results**: Green (FACT), Orange (MYTH), Red (SCAM)
- **Detailed Explanations**: AI-generated reasoning for all verdicts
- **File Management**: Preview, manage, and remove uploaded files

---

*MYTH CHASER - Fighting misinformation with artificial intelligence* 🤖✨