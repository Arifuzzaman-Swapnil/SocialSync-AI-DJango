"""
PDF Processor Service
Extracts text from PDFs and chunks it for RAG
"""
# messenger_bot\services\pdf_processor.py

import PyPDF2
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF text extraction and intelligent chunking
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            dict: {
                'text': str,
                'total_pages': int,
                'metadata': dict
            }
        """
        try:
            text = ""
            metadata = {}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                    }
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                logger.info(f"Extracted {len(text)} characters from {total_pages} pages")
                
                return {
                    'text': text,
                    'total_pages': total_pages,
                    'metadata': metadata
                }
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\(\)\[\]\'\"]+', '', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, page_number: int = None) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            page_number: Optional page number
            
        Returns:
            List of chunks with metadata
        """
        # Clean text first
        text = self.clean_text(text)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings (., !, ?)
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclamation = text.rfind('!', start, end)
                
                # Use the latest sentence ending
                sentence_end = max(last_period, last_question, last_exclamation)
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'page_number': page_number,
                    'start_char': start,
                    'end_char': end,
                    'length': len(chunk_text)
                })
                
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of processed chunks with metadata
        """
        try:
            # Extract text
            extraction_result = self.extract_text_from_pdf(pdf_path)
            
            # Chunk text
            chunks = self.chunk_text(extraction_result['text'])
            
            # Add PDF metadata to each chunk
            for chunk in chunks:
                chunk['total_pages'] = extraction_result['total_pages']
                chunk['pdf_metadata'] = extraction_result['metadata']
            
            logger.info(f"Successfully processed PDF: {len(chunks)} chunks created")
            return chunks
        
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise


# Utility function for quick processing
def process_pdf_file(pdf_path: str, chunk_size: int = 1000) -> List[Dict[str, any]]:
    """
    Quick utility to process a PDF file
    
    Args:
        pdf_path: Path to PDF file
        chunk_size: Size of each chunk
        
    Returns:
        List of processed chunks
    """
    processor = PDFProcessor(chunk_size=chunk_size)
    return processor.process_pdf(pdf_path)