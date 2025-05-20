import tiktoken
import re
from typing import Dict, List, Optional, Tuple

class TokenCounter:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the token counter with a specific model.
        
        Args:
            model (str): The model to use for token counting. Defaults to "gpt-3.5-turbo"
        """
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Compile regex patterns for text segmentation
        self.sentence_endings = re.compile(r'[.!?]+["\']?\s+')
        self.paragraph_breaks = re.compile(r'\n\s*\n')

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))

    def count_tokens_in_messages(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in a list of message dictionaries (as used in chat completions).
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            
        Returns:
            int: Total number of tokens
        """
        total_tokens = 0
        for message in messages:
            # Add tokens for role and content
            total_tokens += self.count_tokens(message["role"])
            total_tokens += self.count_tokens(message["content"])
            # Add 4 tokens for the message structure
            total_tokens += 4
        # Add 3 tokens for the final message
        total_tokens += 3
        return total_tokens

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving sentence boundaries.
        
        Args:
            text (str): The text to split
            
        Returns:
            List[str]: List of sentences
        """
        # Split on sentence endings
        sentences = self.sentence_endings.split(text)
        # Filter out empty sentences and strip whitespace
        return [s.strip() for s in sentences if s.strip()]

    def create_chunk_with_overlap(self, sentences: List[str], max_tokens: int, overlap_tokens: int) -> Tuple[str, int]:
        """
        Create a chunk from sentences with overlap handling.
        
        Args:
            sentences (List[str]): List of sentences to process
            max_tokens (int): Maximum tokens per chunk
            overlap_tokens (int): Number of tokens to overlap between chunks
            
        Returns:
            Tuple[str, int]: The chunk text and the number of sentences used
        """
        chunk = []
        current_tokens = 0
        sentences_used = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed the limit (accounting for overlap)
            if current_tokens + sentence_tokens > max_tokens - overlap_tokens:
                break
                
            chunk.append(sentence)
            current_tokens += sentence_tokens
            sentences_used += 1
        
        return " ".join(chunk), sentences_used

    def chunk_text(self, text: str, max_tokens: int, overlap_tokens: int = 100) -> List[str]:
        """
        Split text into chunks that don't exceed max_tokens, with overlap between chunks.
        
        Args:
            text (str): The text to chunk
            max_tokens (int): Maximum tokens per chunk
            overlap_tokens (int): Number of tokens to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        # Split text into sentences
        sentences = self.split_into_sentences(text)
        chunks = []
        
        # Process sentences into chunks
        current_pos = 0
        while current_pos < len(sentences):
            # Create a chunk with overlap
            chunk, sentences_used = self.create_chunk_with_overlap(
                sentences[current_pos:],
                max_tokens,
                overlap_tokens
            )
            
            if not chunk:  # If we couldn't create a chunk, break
                break
                
            chunks.append(chunk)
            current_pos += max(1, sentences_used - 1)  # Move forward, accounting for overlap
        
        return chunks

    def chunk_text_by_paragraphs(self, text: str, max_tokens: int, overlap_paragraphs: int = 1) -> List[str]:
        """
        Split text into chunks based on paragraphs, with overlap between chunks.
        
        Args:
            text (str): The text to chunk
            max_tokens (int): Maximum tokens per chunk
            overlap_paragraphs (int): Number of paragraphs to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        # Split text into paragraphs
        paragraphs = [p.strip() for p in self.paragraph_breaks.split(text) if p.strip()]
        chunks = []
        
        current_pos = 0
        while current_pos < len(paragraphs):
            chunk_paragraphs = []
            current_tokens = 0
            
            # Add paragraphs until we reach the token limit
            while current_pos < len(paragraphs):
                paragraph = paragraphs[current_pos]
                paragraph_tokens = self.count_tokens(paragraph)
                
                if current_tokens + paragraph_tokens > max_tokens:
                    break
                    
                chunk_paragraphs.append(paragraph)
                current_tokens += paragraph_tokens
                current_pos += 1
            
            if chunk_paragraphs:
                chunks.append("\n\n".join(chunk_paragraphs))
            
            # Move back for overlap
            current_pos = max(0, current_pos - overlap_paragraphs)
        
        return chunks

    def estimate_cost(self, num_tokens: int, model: Optional[str] = None) -> float:
        """
        Estimate the cost of processing a given number of tokens.
        
        Args:
            num_tokens (int): Number of tokens
            model (Optional[str]): Model to use for cost calculation. If None, uses self.model
            
        Returns:
            float: Estimated cost in USD
        """
        model = model or self.model
        # Cost per 1K tokens (as of 2024)
        costs = {
            "gpt-3.5-turbo": 0.0005,  # $0.0005 per 1K tokens
            "gpt-4": 0.03,            # $0.03 per 1K tokens
            "gpt-4-turbo": 0.01,      # $0.01 per 1K tokens
        }
        
        cost_per_token = costs.get(model, 0.0005) / 1000  # Convert to cost per token
        return num_tokens * cost_per_token

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Convenience function to count tokens in text.
    
    Args:
        text (str): The text to count tokens for
        model (str): The model to use for token counting
        
    Returns:
        int: Number of tokens
    """
    counter = TokenCounter(model)
    return counter.count_tokens(text)

def chunk_text(text: str, max_tokens: int = 1000, overlap_tokens: int = 100, model: str = "gpt-3.5-turbo") -> List[str]:
    """
    Convenience function to chunk text into token-limited pieces with overlap.
    
    Args:
        text (str): The text to chunk
        max_tokens (int): Maximum tokens per chunk
        overlap_tokens (int): Number of tokens to overlap between chunks
        model (str): The model to use for token counting
        
    Returns:
        List[str]: List of text chunks
    """
    counter = TokenCounter(model)
    return counter.chunk_text(text, max_tokens, overlap_tokens)

def chunk_text_by_paragraphs(text: str, max_tokens: int = 1000, overlap_paragraphs: int = 1, model: str = "gpt-3.5-turbo") -> List[str]:
    """
    Convenience function to chunk text by paragraphs with overlap.
    
    Args:
        text (str): The text to chunk
        max_tokens (int): Maximum tokens per chunk
        overlap_paragraphs (int): Number of paragraphs to overlap between chunks
        model (str): The model to use for token counting
        
    Returns:
        List[str]: List of text chunks
    """
    counter = TokenCounter(model)
    return counter.chunk_text_by_paragraphs(text, max_tokens, overlap_paragraphs) 