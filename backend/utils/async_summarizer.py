import os
import asyncio
import httpx
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Limit concurrent API calls to avoid rate limits
MAX_CONCURRENT_CALLS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

SYSTEM_PROMPT = """You are a helpful assistant that creates concise, well-formatted LaTeX bullet points from text.
Focus on extracting key information and formatting it as LaTeX bullet points.
Format your response as a complete LaTeX itemize environment:

\\begin{itemize}
\\item First bullet point
\\item Second bullet point
\\item Third bullet point
\\end{itemize}

Do not include any other LaTeX document structure or preamble - only return the itemize environment with bullet points.
Use \\item for each bullet point and maintain proper LaTeX formatting."""

async def summarize_chunk(client: httpx.AsyncClient, chunk: str) -> str:
    """Summarize a single chunk of text using OpenAI's API"""
    async with semaphore:  # Limit concurrent API calls
        try:
            logger.info(f"Processing chunk of length {len(chunk)}")
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": chunk}
                    ],
                    "temperature": 0.7
                },
                timeout=30.0  # Add timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit error
                logger.warning("Rate limit hit, waiting 60 seconds before retry")
                await asyncio.sleep(60)  # Wait for 60 seconds
                return await summarize_chunk(client, chunk)  # Retry the request
            logger.error(f"HTTP error occurred: {str(e)}")
            raise
        except httpx.TimeoutException:
            logger.error("Request timed out")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

async def summarize_all_chunks(chunks: List[str]) -> List[str]:
    """Process all chunks concurrently using httpx with rate limiting"""
    try:
        async with httpx.AsyncClient() as client:
            tasks = [summarize_chunk(client, chunk) for chunk in chunks]
            return await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in summarize_all_chunks: {str(e)}")
        raise 