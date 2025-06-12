# 🔧 MYTH CHASER API

**AI-powered backend for fact-checking and anti-scam detection**

The MYTH CHASER API is a sophisticated FastAPI-based backend that orchestrates multiple AI models and external services to provide comprehensive content verification and fact-checking capabilities.

## 🌟 Features

### 🔌 API Endpoints

#### `POST /classify`
**Main content verification endpoint**
- **Input**: 
  - Text prompt (required)
  - File uploads (optional: images, audio)
  - Source language (optional: auto, en, fr, ar, tunisian_ar, transliterated_ar)
- **Output**: Structured response with verdict and explanation
- **Processing**: Multi-threaded analysis using 7 AI models
- **Response Format**:
  ```json
  {
    "Success": {
      "Verdict": "FACT|MYTH|SCAM",
      "Explanation": "Detailed AI-generated explanation",
      "OriginalLanguage": "detected language",
      "Confidence": 0.0-1.0
    }
  }
  ```

### 🤖 AI Model Ensemble

#### Natural Language Inference (NLI)
- **Model**: `ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli`
- **Purpose**: Logical reasoning between claims and evidence
- **Output**: Entailment/Neutral/Contradiction classification
- **Integration**: Averages predictions across multiple evidence sources

#### Sentence-BERT (SBERT)
- **Model**: `all-MiniLM-L6-v2`
- **Purpose**: Semantic similarity analysis
- **Method**: Cosine similarity between claim and evidence embeddings
- **Thresholds**: >0.7 (FACT), 0.4-0.7 (MYTH), <0.4 (SCAM)

#### ClaimBuster Integration
- **Service**: University of Texas ClaimBuster API
- **Purpose**: Professional fact-checking database access
- **Scoring**: 0-1 claim worthiness score
- **Classification**: ≥0.5 (FACT), 0.25-0.5 (MYTH), <0.25 (SCAM)

#### Google Fact Check API
- **Service**: Google Fact Check Tools API
- **Purpose**: Access to global fact-checking organizations
- **Processing**: Aggregates multiple fact-checker verdicts
- **Mapping**: Textual ratings to numerical scores

#### Fake News Detection
- **Model**: `winterForestStump/Roberta-fake-news-detector`
- **Purpose**: Specialized misinformation pattern detection
- **Confidence-based**: High confidence FAKE → SCAM, Low confidence → MYTH

#### TunBERT Model
- **Model**: `not-lain/TunBERT`
- **Purpose**: Arabic and Tunisian dialect fact-checking
- **Integration**: Direct processing of Arabic text
- **Confidence**: Threshold-based classification (0.6)

#### Groq LLM Integration
- **Model**: `Groq Qwen3-32B`
- **Purpose**: Advanced reasoning and verdict generation
- **Weight**: 3x voting power in ensemble
- **Features**: 
  - Sophisticated claim analysis
  - Evidence-based reasoning
  - Detailed explanation generation
  - Rate-limited API management (50 req/60s)

### 📁 Media Processing Pipeline

#### Image Analysis (`converters/text_from_image.py`)
- **OCR**: Pytesseract for text extraction
- **Captioning**: BLIP model for visual content description
- **Output**: Combined textual representation

#### Audio Processing (`converters/text_from_audio.py`)
- **Formats**: WAV, FLAC, AIFF, AIFC
- **Error Handling**: Graceful degradation for unclear audio

### 🌐 Web Search Integration

#### Evidence Gathering (`web_searcher/app.py`)
- **Search Engine**: DuckDuckGo search integration
- **Processing**: Intelligent snippet extraction and cleaning
- **Aggregation**: Combines multiple sources into coherent paragraphs
- **Scalability**: Configurable number of results and paragraphs

### ⚡ Performance Optimizations

#### Multi-threading Architecture
- **Parallel Processing**: All AI models run concurrently
- **Thread Safety**: Proper isolation and result aggregation
- **Timeout Handling**: Graceful handling of slow models

#### Voting Algorithm
- **Consensus Building**: Weighted voting across all model predictions
- **Uncertainty Handling**: Ignores uncertain/unknown predictions
- **Tie Breaking**: Defaults to most conservative classification

#### Error Management
- **Graceful Degradation**: Individual model failures don't crash the system
- **Fallback Responses**: Meaningful error messages for users
- **Logging**: Comprehensive error tracking and debugging

## 🛠️ Technical Stack

### Core Framework
- **FastAPI**: High-performance async web framework
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

### AI/ML Libraries
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face model hub integration
- **Sentence-Transformers**: Specialized embedding models
- **Groq Python SDK**: LLM API integration
- **PIL**: Image processing capabilities
- **SpeechRecognition**: Audio processing toolkit

### External Services
- **ClaimBuster API**: Professional fact-checking service
- **Google Fact Check API**: Global fact-checking database
- **DuckDuckGo Search**: Privacy-focused web search
- **Google Translate**: Multi-language translation

### Utilities
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for API integrations
- **pytesseract**: OCR text extraction
- **googletrans**: Translation library
- **spacy**: Advanced NLP preprocessing

## 📂 Project Structure

```
apis/
├── main.py                  # FastAPI application and main endpoint
├── requirements.txt         # Python dependencies
│
├── models/                  # AI model implementations
│   ├── NLI/model.py        # Natural Language Inference
│   ├── SBERT/model.py      # Sentence-BERT similarity
│   ├── ClaimBuster/model.py # ClaimBuster API client
│   ├── Google/model.py     # Google Fact Check client
│   ├── FakeNewsDetector/   # Fake news classification
│   └── Explainer/model.py  # AI explanation generation
│
├── converters/             # Media-to-text conversion
│   ├── __init__.py        # Package initialization
│   ├── converter.py       # Main conversion orchestrator
│   ├── text_from_image.py # Image analysis and OCR
│   ├── text_from_audio.py # Speech-to-text conversion
│   └── text_from_text.py  # Text file processing
│
└── web_searcher/          # Evidence gathering
    └── app.py             # Web search and content aggregation
```

## 🔧 Configuration

### Environment Variables
```bash
CLAIMBUSTER_API_KEY=your_claimbuster_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Model Loading
- **Automatic**: Models load on first import
- **Caching**: Models remain in memory for performance
- **GPU Support**: CUDA acceleration where available

## 🚀 Performance Characteristics

- **Response Time**: 5-15 seconds typical (depends on model loading)
- **Concurrency**: Multi-threaded processing for 5 models
- **Memory Usage**: ~4-8GB RAM (varies by model size)
- **GPU Utilization**: Automatic CUDA detection and usage
- **Error Rate**: <1% (robust error handling throughout)