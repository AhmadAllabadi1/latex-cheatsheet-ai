import re
from typing import List, Tuple

class TextSanitizer:
    def __init__(self):
        # Common patterns to remove
        self.patterns = [
            # Page numbers (various formats)
            r'^\s*\d+\s*$',  # Standalone page numbers
            r'Page\s+\d+',   # "Page X" format
            r'-\s*\d+\s*-',  # "- X -" format
            
            # Headers and footers
            r'^\s*[A-Z][A-Za-z\s]+\s*$',  # All caps or title case lines
            r'^\s*©.*$',     # Copyright notices
            r'^\s*www\..*$', # Website URLs
            
            # Enhanced copyright and legal patterns
            r'^\s*Copyright\s+©\s*\d{4}.*$',  # Copyright © 2024 format
            r'^\s*All rights reserved.*$',     # All rights reserved
            r'^\s*This document is confidential.*$',  # Confidentiality notices
            r'^\s*Proprietary and confidential.*$',   # Proprietary notices
            r'^\s*Unauthorized copying.*$',          # Unauthorized copying notices
            r'^\s*For internal use only.*$',         # Internal use notices
            r'^\s*Protected by copyright law.*$',    # Copyright law notices
            r'^\s*[A-Z\s]+CONFIDENTIAL.*$',         # CONFIDENTIAL headers
            r'^\s*[A-Z\s]+RESTRICTED.*$',           # RESTRICTED headers
            r'^\s*[A-Z\s]+PRIVATE.*$',              # PRIVATE headers
            r'^\s*[A-Z\s]+INTERNAL.*$',             # INTERNAL headers
            r'^\s*[A-Z\s]+CONFIDENTIALITY.*$',      # CONFIDENTIALITY headers
            r'^\s*[A-Z\s]+PROPRIETARY.*$',          # PROPRIETARY headers
            r'^\s*[A-Z\s]+TRADE SECRET.*$',         # TRADE SECRET headers
            r'^\s*[A-Z\s]+CLASSIFIED.*$',           # CLASSIFIED headers
            r'^\s*[A-Z\s]+SENSITIVE.*$',            # SENSITIVE headers
            r'^\s*[A-Z\s]+RESTRICTED ACCESS.*$',    # RESTRICTED ACCESS headers
            r'^\s*[A-Z\s]+FOR INTERNAL USE.*$',     # FOR INTERNAL USE headers
            r'^\s*[A-Z\s]+NOT FOR DISTRIBUTION.*$', # NOT FOR DISTRIBUTION headers
            r'^\s*[A-Z\s]+CONFIDENTIAL DOCUMENT.*$',# CONFIDENTIAL DOCUMENT headers
            r'^\s*[A-Z\s]+PROPRIETARY INFORMATION.*$', # PROPRIETARY INFORMATION headers
            r'^\s*[A-Z\s]+TRADE SECRET INFORMATION.*$', # TRADE SECRET INFORMATION headers
            r'^\s*[A-Z\s]+CLASSIFIED INFORMATION.*$',   # CLASSIFIED INFORMATION headers
            r'^\s*[A-Z\s]+SENSITIVE INFORMATION.*$',    # SENSITIVE INFORMATION headers
            r'^\s*[A-Z\s]+RESTRICTED INFORMATION.*$',   # RESTRICTED INFORMATION headers
            r'^\s*[A-Z\s]+FOR INTERNAL USE ONLY.*$',    # FOR INTERNAL USE ONLY headers
            r'^\s*[A-Z\s]+NOT FOR PUBLIC DISTRIBUTION.*$', # NOT FOR PUBLIC DISTRIBUTION headers
            r'^\s*[A-Z\s]+CONFIDENTIAL AND PROPRIETARY.*$', # CONFIDENTIAL AND PROPRIETARY headers
            r'^\s*[A-Z\s]+TRADE SECRET AND CONFIDENTIAL.*$', # TRADE SECRET AND CONFIDENTIAL headers
            r'^\s*[A-Z\s]+CLASSIFIED AND RESTRICTED.*$',    # CLASSIFIED AND RESTRICTED headers
            r'^\s*[A-Z\s]+SENSITIVE AND CONFIDENTIAL.*$',   # SENSITIVE AND CONFIDENTIAL headers
            r'^\s*[A-Z\s]+RESTRICTED AND PROPRIETARY.*$',   # RESTRICTED AND PROPRIETARY headers
            r'^\s*[A-Z\s]+FOR INTERNAL USE AND CONFIDENTIAL.*$', # FOR INTERNAL USE AND CONFIDENTIAL headers
            r'^\s*[A-Z\s]+NOT FOR PUBLIC DISTRIBUTION AND CONFIDENTIAL.*$', # NOT FOR PUBLIC DISTRIBUTION AND CONFIDENTIAL headers
            
            # Footnotes and references
            r'^\s*\d+\.\s*$',  # Numbered footnotes
            r'^\s*\[\d+\]\s*', # [1] style references
            r'^\s*\*\s*$',     # Asterisk footnotes
            
            # Common PDF artifacts
            r'^\s*[•\-\*]{3,}\s*$',  # Separator lines
            r'^\s*\.{3,}\s*$',       # Dotted lines
            r'^\s*_{3,}\s*$',        # Underscore lines
            
            # Empty or whitespace-only lines
            r'^\s*$'
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.MULTILINE) for pattern in self.patterns]
        
        # Patterns to clean up but not remove entirely
        self.cleanup_patterns = [
            # Multiple spaces
            (r'\s+', ' '),
            # Multiple newlines
            (r'\n{3,}', '\n\n'),
            # Spaces before punctuation
            (r'\s+([.,;:!?])', r'\1'),
            # Spaces after opening and before closing brackets
            (r'\(\s+', '('),
            (r'\s+\)', ')'),
            (r'\[\s+', '['),
            (r'\s+\]', ']'),
            # Strange bullets and formatting artifacts
            (r'[•»–]{1,3}', '')
        ]
        
        # Compile cleanup patterns
        self.compiled_cleanup = [(re.compile(pattern), repl) for pattern, repl in self.cleanup_patterns]

    def remove_noise(self, text: str) -> str:
        """Remove common noise patterns from text"""
        # Apply removal patterns
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        return text

    def cleanup_text(self, text: str) -> str:
        """Clean up text formatting without removing content"""
        # Apply cleanup patterns
        for pattern, repl in self.compiled_cleanup:
            text = pattern.sub(repl, text)
        return text

    def sanitize(self, text: str) -> str:
        """Apply all sanitization steps to the text"""
        # First remove noise
        text = self.remove_noise(text)
        # Then clean up formatting
        text = self.cleanup_text(text)
        # Finally, ensure consistent line endings and remove extra whitespace
        text = text.strip()
        return text

    def process_section(self, text: str) -> str:
        """Process a section of text, preserving structure but removing noise"""
        # Split into lines
        lines = text.split('\n')
        # Process each line
        processed_lines = []
        for line in lines:
            # Skip lines that match noise patterns
            if not any(pattern.match(line) for pattern in self.compiled_patterns):
                processed_lines.append(line)
        
        # Join lines and clean up
        return self.cleanup_text('\n'.join(processed_lines))

def sanitize_text(text: str) -> str:
    """Convenience function to sanitize text using the default sanitizer"""
    sanitizer = TextSanitizer()
    return sanitizer.sanitize(text) 