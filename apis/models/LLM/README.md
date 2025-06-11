# Groq Qwen3-32B Integration for AINS Fact Checker

This module integrates Groq's Qwen2.5-32B model into the AINS (Anti-scam Intelligence System) for advanced claim verification.

## Features

- **Advanced Reasoning**: Uses Qwen2.5-32B model for sophisticated claim analysis
- **Source Integration**: Analyzes claims against web-searched sources
- **Confidence Scoring**: Provides confidence levels for classifications
- **Detailed Explanations**: Returns reasoning and key evidence points
- **Ensemble Voting**: Integrates with existing models in the voting system

## Setup

### 1. Install Dependencies

```bash
pip install groq python-dotenv
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Generate an API key
4. Copy your API key (starts with `gsk_`)

### 3. Configure Environment

Create a `.env` file in the `apis` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
CLAIMBUSTER_API_KEY=your_claimbuster_key
GOOGLE_API_KEY=your_google_key
```

## Usage

### Basic Claim Verification

```python
from models.LLM.groq import quick_verify

result = quick_verify("The Earth is flat")
print(result)  # Returns: MYTH
```

### Advanced Analysis with Sources

```python
from models.LLM.groq import groq_fact_check, get_detailed_groq_analysis
from web_searcher.app import search_topic

# Get sources
sources = search_topic("5G causes cancer", num_paragraphs=5)

# Simple classification
result = groq_fact_check("5G causes cancer", sources)
print(result)  # Returns: MYTH

# Detailed analysis
detailed = get_detailed_groq_analysis("5G causes cancer", sources)
print(detailed)
# Returns detailed JSON with classification, confidence, reasoning, etc.
```

### API Endpoints

The integration adds new endpoints to the FastAPI server:

#### GET `/groq-analyze`

Get detailed analysis from Groq model.

**Parameters:**

- `prompt` (str): The claim to analyze
- `include_sources` (bool): Whether to search for web sources

**Response:**

```json
{
  "claim": "Your claim here",
  "simple_classification": "FACT|MYTH|SCAM",
  "detailed_analysis": {
    "classification": "MYTH",
    "confidence": 0.85,
    "reasoning": "Detailed explanation...",
    "key_evidence": ["evidence point 1", "evidence point 2"],
    "model": "Groq Qwen2.5-32B"
  },
  "sources_used": 5,
  "timestamp": "2025-06-11"
}
```

#### GET `/models/status`

Check availability of all models including Groq.

## Model Integration

The Groq model is integrated into the ensemble voting system:

1. **NLI Model**: Natural Language Inference
2. **ClaimBuster**: Fact-checking API
3. **SBERT**: Sentence similarity
4. **Google Fact Check**: Google's fact-checking API
5. **TunBERT**: Specialized fact-checking model
6. **Groq Qwen2.5-32B**: Advanced reasoning model _(NEW)_

Each model votes, and the final classification is determined by majority vote.

## Classification Categories

- **FACT**: Claim is factually accurate and supported by evidence
- **MYTH**: Claim is false, misleading, or lacks sufficient evidence
- **SCAM**: Claim appears deliberately deceptive or fraudulent
- **UNCERTAIN**: Insufficient confidence or conflicting evidence

## Testing

Run the test script to verify your setup:

```bash
python test_groq.py
```

This will test:

- API key configuration
- Basic claim verification
- Analysis with web sources
- Error handling

## Configuration Options

### Model Parameters

The Groq integration uses these settings:

```python
completion = client.chat.completions.create(
    model="qwen2.5-32b-instruct",
    temperature=0.1,  # Low for consistent results
    max_tokens=1024,
    top_p=0.9
)
```

### Confidence Thresholds

- **High Confidence**: ≥ 0.7
- **Medium Confidence**: 0.4 - 0.7
- **Low Confidence**: < 0.4 (returns UNCERTAIN)

## Prompt Engineering

The system uses carefully crafted prompts for optimal results:

```
You are an expert fact-checker with access to reliable information sources.
Your task is to analyze the following claim and determine its veracity.

CLAIM TO VERIFY: "{claim}"
{context from sources}

Please analyze this claim thoroughly and provide:
1. CLASSIFICATION: FACT|MYTH|SCAM
2. CONFIDENCE: 0.0 to 1.0
3. REASONING: Clear explanation
4. KEY_EVIDENCE: Important evidence points
```

## Error Handling

The integration includes robust error handling:

- API failures fallback to UNCERTAIN
- JSON parsing errors extract classification from text
- Network timeouts handled gracefully
- Invalid responses mapped to safe defaults

## Performance

- **Response Time**: ~2-5 seconds per claim
- **Batch Processing**: Supported for multiple claims
- **Rate Limiting**: Respects Groq API limits
- **Caching**: Can be added for repeated claims

## Troubleshooting

### Common Issues

1. **API Key Error**

   ```
   Error: Invalid API key
   ```

   - Check your `.env` file has the correct GROQ_API_KEY
   - Ensure the key starts with `gsk_`

2. **Import Error**

   ```
   ModuleNotFoundError: No module named 'groq'
   ```

   - Install the groq package: `pip install groq`

3. **Classification Returns UNCERTAIN**
   - Check if API key is valid
   - Verify internet connection
   - Try with simpler claims first

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To improve the Groq integration:

1. Adjust prompt templates in `classify_claim_with_groq()`
2. Modify confidence thresholds
3. Add new analysis features
4. Optimize for specific claim types

## License

This integration follows the same license as the AINS project.
