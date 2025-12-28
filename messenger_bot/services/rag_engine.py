"""
RAG Engine Service
Retrieval-Augmented Generation core logic
"""
# messenger_bot\services\rag_engine.py

import logging
from typing import List, Dict, Optional
from django.db import transaction

from ..models import PDFKnowledgeBase, PDFChunk, AIConfiguration
from .pdf_processor import PDFProcessor
from .openai_client import OpenAIClient, find_most_similar

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Handles RAG (Retrieval-Augmented Generation) operations
    """
    
    def __init__(self, ai_config: AIConfiguration):
        """
        Initialize RAG engine
        
        Args:
            ai_config: AIConfiguration instance
        """
        self.ai_config = ai_config
        self.openai_client = OpenAIClient(api_key=ai_config.openai_api_key)
        self.pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
    
    def process_pdf(self, pdf_knowledge_base: PDFKnowledgeBase) -> bool:
        """
        Process a PDF and store chunks with embeddings
        
        Args:
            pdf_knowledge_base: PDFKnowledgeBase instance
            
        Returns:
            bool: Success status
        """
        try:
            # Update status
            pdf_knowledge_base.status = 'processing'
            pdf_knowledge_base.save()
            
            logger.info(f"Processing PDF: {pdf_knowledge_base.filename}")
            
            # Extract and chunk text
            chunks = self.pdf_processor.process_pdf(pdf_knowledge_base.file.path)
            
            if not chunks:
                raise ValueError("No text extracted from PDF")
            
            logger.info(f"Created {len(chunks)} chunks from PDF")
            
            # Create embeddings for all chunks
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = self.openai_client.create_embeddings_batch(
                chunk_texts,
                model=self.ai_config.embedding_model
            )
            
            logger.info(f"Created {len(embeddings)} embeddings")
            
            # Store chunks with embeddings in database
            with transaction.atomic():
                # Delete existing chunks if any
                PDFChunk.objects.filter(pdf=pdf_knowledge_base).delete()
                
                # Create new chunks
                pdf_chunks = []
                for chunk_data, embedding in zip(chunks, embeddings):
                    pdf_chunk = PDFChunk(
                        pdf=pdf_knowledge_base,
                        text=chunk_data['text'],
                        chunk_index=chunk_data['chunk_index'],
                        page_number=chunk_data.get('page_number'),
                    )
                    pdf_chunk.set_embedding(embedding)
                    pdf_chunks.append(pdf_chunk)
                
                # Bulk create
                PDFChunk.objects.bulk_create(pdf_chunks)
                
                # Update PDF status
                pdf_knowledge_base.status = 'completed'
                pdf_knowledge_base.total_chunks = len(chunks)
                pdf_knowledge_base.total_pages = chunks[0].get('total_pages', 0)
                pdf_knowledge_base.vectorized_at = timezone.now()
                pdf_knowledge_base.save()
            
            logger.info(f"Successfully processed PDF: {pdf_knowledge_base.filename}")
            return True
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_knowledge_base.filename}: {e}")
            
            # Update error status
            pdf_knowledge_base.status = 'failed'
            pdf_knowledge_base.error_message = str(e)
            pdf_knowledge_base.save()
            
            return False
    
    def retrieve_relevant_chunks(
        self,
        query: str,
        connection,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, any]]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query
            connection: MessengerConnection instance
            top_k: Number of chunks to retrieve (uses ai_config default if None)
            similarity_threshold: Minimum similarity score (uses ai_config default if None)
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Use config defaults if not specified
            if top_k is None:
                top_k = self.ai_config.top_k_results
            if similarity_threshold is None:
                similarity_threshold = self.ai_config.similarity_threshold
            
            logger.info(f"Retrieving chunks for query (top_k={top_k}, threshold={similarity_threshold})")
            
            # Create query embedding
            query_embedding = self.openai_client.create_embedding(
                query,
                model=self.ai_config.embedding_model
            )
            
            # Get all chunks from completed PDFs
            pdf_chunks = PDFChunk.objects.filter(
                pdf__connection=connection,
                pdf__status='completed'
            ).select_related('pdf')
            
            if not pdf_chunks.exists():
                logger.warning("No processed PDF chunks available")
                return []
            
            # Get embeddings and calculate similarities
            chunks_data = []
            for chunk in pdf_chunks:
                chunk_embedding = chunk.get_embedding()
                similarity = self.openai_client.cosine_similarity(query_embedding, chunk_embedding)
                
                if similarity >= similarity_threshold:
                    chunks_data.append({
                        'chunk': chunk,
                        'similarity': similarity,
                        'text': chunk.text,
                        'page_number': chunk.page_number,
                        'filename': chunk.pdf.filename
                    })
            
            # Sort by similarity
            chunks_data.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top k
            relevant_chunks = chunks_data[:top_k]
            
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")
            return relevant_chunks
        
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []
    
    def generate_response(
        self,
        query: str,
        connection,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, any]:
        """
        Generate AI response using RAG
        
        Args:
            query: User query
            connection: MessengerConnection instance
            conversation_history: Optional conversation history
            
        Returns:
            dict: {
                'response': str,
                'context_used': str,
                'model': str,
                'tokens': int
            }
        """
        try:
            # Retrieve relevant chunks
            relevant_chunks = []
            context_text = ""
            
            if self.ai_config.rag_enabled:
                relevant_chunks = self.retrieve_relevant_chunks(query, connection)
                
                if relevant_chunks:
                    # Build context from chunks
                    context_parts = []
                    for i, chunk_data in enumerate(relevant_chunks):
                        context_parts.append(
                            f"[Source {i+1}: {chunk_data['filename']}, "
                            f"Page {chunk_data['page_number'] or 'N/A'}]\n"
                            f"{chunk_data['text']}\n"
                        )
                    context_text = "\n".join(context_parts)
                    logger.info(f"Using {len(relevant_chunks)} chunks as context")
            
            # Get active prompt
            active_prompt = connection.prompts.filter(is_active=True).first()
            system_prompt = active_prompt.system_prompt if active_prompt else (
                "You are a helpful AI assistant."
            )
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add context and query
            if context_text:
                user_message = (
                    f"Based on the following information:\n\n{context_text}\n\n"
                    f"Please answer this question: {query}"
                )
            else:
                user_message = query
            
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = self.openai_client.chat_completion(
                messages=messages,
                model=self.ai_config.openai_model,
                temperature=self.ai_config.temperature,
                max_tokens=self.ai_config.max_tokens
            )
            
            return {
                'response': response['content'],
                'context_used': context_text,
                'model': response['model'],
                'tokens': response['tokens'],
                'chunks_used': len(relevant_chunks)
            }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': "I'm sorry, I encountered an error while processing your request.",
                'context_used': "",
                'model': self.ai_config.openai_model,
                'tokens': 0,
                'chunks_used': 0,
                'error': str(e)
            }


# Import timezone for the vectorized_at field
from django.utils import timezone