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
- **Groq Qwen3-32B**: Advanced large language model with sophisticated reasoning capabilities
- **TunBERT**: Specialized Arabic and Tunisian dialect fact-checking model
- **AI Explanation Generator**: Groq-powered detailed explanations for all verdicts

### 🔍 Multi-Format Content Analysis
- **Text Processing**: Direct text input analysis and verification
- **Image Analysis**: OCR text extraction and visual content description using BLIP
- **Audio Processing**: Speech-to-text conversion for audio content verification
- **Drag & Drop Interface**: Seamless file upload with support for multiple formats

### 🌐 Multi-Language Support
- **Auto-Detection**: Automatic language identification for incoming content
- **Translation Engine**: Google Translate integration for seamless cross-language analysis
- **Arabic Dialect Support**: Specialized handling for Tunisian Arabic and transliterated text
- **Language Preservation**: Original text maintained for dialect-specific models

### 🌐 Real-Time Web Search
- **DuckDuckGo Integration**: Automated web search for evidence gathering
- **Source Aggregation**: Intelligent collection and processing of relevant information
- **Evidence Synthesis**: Combines multiple sources for comprehensive analysis

### 🎯 Three-Tier Classification System
- **FACT**: Verified true statements with supporting evidence
- **MYTH**: Partially true or misleading information requiring clarification
- **SCAM**: False, harmful, or deceptive content

### 💡 Advanced Weighted Voting Algorithm
- **Multi-Model Consensus**: Combines predictions from 7 specialized AI models
- **Intelligent Weighting**: Groq Qwen3-32B receives highest voting power (3x weight)
- **Confidence-Based Filtering**: Ignores uncertain predictions for cleaner results
- **Graceful Degradation**: System continues functioning even with individual model failures

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
- **Large Language Models**: Groq Qwen3-32B for advanced reasoning and explanation
- **Specialized Dialects**: TunBERT for Arabic and Tunisian language support
- **Computer Vision**: BLIP model for image understanding
- **Speech Recognition**: Google Speech Recognition for audio processing
- **Ensemble Methods**: Multiple model predictions combined for accuracy

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PyTorch**: Deep learning framework for AI models
- **Transformers**: Hugging Face transformers library
- **Groq**: Advanced LLM API integration
- **SpeechRecognition**: Audio processing capabilities
- **PIL/Pytesseract**: Image processing and OCR
- **GoogleTrans**: Multi-language translation support
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
- **not-lain/TunBERT**: Arabic and Tunisian dialect fact-checking
- **Groq Qwen3-32B**: Advanced reasoning and explanation generation
- **Salesforce/blip-image-captioning-base**: Image captioning

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