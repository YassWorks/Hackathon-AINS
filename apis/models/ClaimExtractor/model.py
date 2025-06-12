from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import List, Union
import logging

# Setup logging
logger = logging.getLogger(__name__)

class ClaimExtractor:
    """
    A class for extracting claims from text summaries using T5-based model.
    """
    
    def __init__(self, model_name: str = "Babelscape/t5-base-summarization-claim-extractor"):
        """
        Initialize the ClaimExtractor with the specified model.
        
        Args:
            model_name (str): The name/path of the pre-trained model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the tokenizer and model."""
        try:
            logger.info(f"Loading tokenizer and model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def extract_claims(self, 
                      text: Union[str, List[str]], 
                      max_length: int = 512,
                      num_beams: int = 4,
                      temperature: float = 1.0,
                      do_sample: bool = False) -> List[str]:
        """
        Extract claims from the given text(s).
        
        Args:
            text (Union[str, List[str]]): The input text(s) to extract claims from
            max_length (int): Maximum length of generated claims
            num_beams (int): Number of beams for beam search
            temperature (float): Temperature for sampling
            do_sample (bool): Whether to use sampling instead of greedy decoding
            
        Returns:
            List[str]: List of extracted claims
        """
        if self.tokenizer is None or self.model is None:
            raise RuntimeError("Model not properly initialized")
        
        # Handle single string input
        if isinstance(text, str):
            text = [text]
        
        try:
            # Tokenize input
            tok_input = self.tokenizer.batch_encode_plus(
                text, 
                return_tensors="pt", 
                padding=True,
                truncation=True,
                max_length=max_length
            )
            
            # Generate claims
            try:
                import torch
                context_manager = torch.no_grad()
            except ImportError:
                # Fallback if torch is not available
                from contextlib import nullcontext
                context_manager = nullcontext()
            
            with context_manager:
                claims = self.model.generate(
                    **tok_input,
                    max_length=max_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    do_sample=do_sample,
                    early_stopping=True
                )
            
            # Decode claims
            decoded_claims = self.tokenizer.batch_decode(claims, skip_special_tokens=True)
            logger.debug(f"Decoded claims: {decoded_claims}")
            print(f"Decoded claims: {decoded_claims}")

            all_extracted_claims: List[str] = []
            for decoded_text_block in decoded_claims:
                if decoded_text_block.strip(): # Ensure block is not empty or just whitespace
                    individual_claims_from_block = self.__sentance_split(decoded_text_block)
                    all_extracted_claims.extend(individual_claims_from_block)
            
            logger.info(f"Extracted {len(all_extracted_claims)} claims from {len(text)} input text(s)")
            return all_extracted_claims
            
        except Exception as e:
            logger.error(f"Error extracting claims: {e}")
            raise
    def __sentance_split(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text (str): The input text to split
            
        Returns:
            List[str]: List of sentences
        """
        import re
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov|edu|me)"
        digits = "([0-9])"
        multiple_dots = r'\.{2,}'
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
        text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if sentences and not sentences[-1]: sentences = sentences[:-1]
        return sentences

# Global instance for backward compatibility
_claim_extractor = None

def get_claim_extractor() -> ClaimExtractor:
    """
    Get a singleton instance of ClaimExtractor.
    
    Returns:
        ClaimExtractor: The claim extractor instance
    """
    global _claim_extractor
    if _claim_extractor is None:
        _claim_extractor = ClaimExtractor()
    return _claim_extractor

def extract_claims_from_text(text: Union[str, List[str]], **kwargs) -> List[str]:
    """
    Convenience function to extract claims from text.
    
    Args:
        text (Union[str, List[str]]): The input text(s) to extract claims from
        **kwargs: Additional arguments passed to ClaimExtractor.extract_claims()
        
    Returns:
        List[str]: List of extracted claims
    """
    extractor = get_claim_extractor()
    return extractor.extract_claims(text, **kwargs)

# Example usage (can be run as script)
if __name__ == "__main__":
    # Example text
    summary = ('Simone Biles made a triumphant return to the Olympic stage at the Paris 2024 Games, '
              'competing in the women\'s gymnastics qualifications. Overcoming a previous struggle with '
              'the "twisties" that led to her withdrawal from events at the Tokyo 2020 Olympics, Biles '
              'dazzled with strong performances on all apparatus, helping the U.S. team secure a commanding '
              'lead in the qualifications. Her routines showcased her resilience and skill, drawing '
              'enthusiastic support from a star-studded audience')
    
    # Extract claims
    claims = extract_claims_from_text(summary)
    
    print("Extracted Claims:")
    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim}")
