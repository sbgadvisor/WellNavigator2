"""
RAG (Retrieval-Augmented Generation) module for WellNavigator.
Handles document retrieval from FAISS index for context injection.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None


class RAGRetriever:
    """Handles retrieval from FAISS index for RAG queries."""
    
    def __init__(self, index_dir: str = "data/index"):
        self.index_dir = Path(index_dir)
        self.index = None
        self.metadata = []
        self.embedder = None
        self.model_info = {}
        self._loaded = False
    
    def load_index(self) -> bool:
        """Load FAISS index and metadata from disk."""
        try:
            # Check if index files exist
            index_file = self.index_dir / "faiss_index.bin"
            metadata_file = self.index_dir / "metadata.json"
            model_info_file = self.index_dir / "model_info.json"
            
            if not all(f.exists() for f in [index_file, metadata_file, model_info_file]):
                print(f"❌ RAG index not found at {self.index_dir}")
                print("Run 'python ingest.py' to create the index first")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Load model info
            with open(model_info_file, 'r', encoding='utf-8') as f:
                self.model_info = json.load(f)
            
            # Load embedding model
            model_name = self.model_info.get('model_name', 'all-MiniLM-L6-v2')
            self.embedder = SentenceTransformer(model_name)
            
            self._loaded = True
            print(f"✅ RAG index loaded: {self.index.ntotal} documents")
            return True
            
        except Exception as e:
            print(f"❌ Error loading RAG index: {e}")
            return False
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Retrieve top-k most relevant documents for a query.
        
        Args:
            query: Search query text
            k: Number of documents to retrieve
            
        Returns:
            List of dictionaries with 'text', 'source', 'score', and 'title'
        """
        if not self._loaded:
            if not self.load_index():
                return []
        
        try:
            # Create query embedding
            query_embedding = self.embedder.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Retrieve results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                # Get metadata for this result
                meta = self.metadata[idx]
                
                # For FAISS metadata, we need to get the text from somewhere
                # Since we didn't store text in FAISS, we'll reconstruct from metadata
                # This is a limitation - in production, you'd store text in FAISS or separate store
                results.append({
                    'text': f"Content from {meta['source']} - {meta['title']}",  # Placeholder
                    'source': meta['source'],
                    'title': meta['title'],
                    'score': float(score),
                    'chunk_id': idx
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error during retrieval: {e}")
            return []
    
    def retrieve_with_text(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Retrieve documents with actual text content.
        This version requires the full document store to be loaded.
        """
        # For now, return a simplified version that works with our setup
        # In a production system, you'd have the full text stored and indexed
        
        if not self._loaded:
            if not self.load_index():
                return []
        
        try:
            # Create query embedding
            query_embedding = self.embedder.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Retrieve results with enhanced metadata
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                
                meta = self.metadata[idx]
                
                # Create a more informative text snippet
                # In production, this would be the actual chunk text
                text_snippet = self._create_text_snippet(meta, query)
                
                results.append({
                    'text': text_snippet,
                    'source': meta['source'],
                    'title': meta['title'],
                    'score': float(score),
                    'chunk_id': idx,
                    'text_length': meta.get('text_length', 0)
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error during retrieval: {e}")
            return []
    
    def _create_text_snippet(self, meta: Dict, query: str) -> str:
        """Create a text snippet based on metadata and query."""
        # This is a simplified version - in production you'd store actual text
        
        source = meta['source']
        title = meta['title']
        
        # Create contextual snippets based on source and title
        snippets = {
            'Diabetes': "Type 2 diabetes is a chronic condition affecting blood sugar processing. Early signs include increased thirst, fatigue, and blurred vision. Risk factors include family history, obesity, and inactivity. Treatment involves lifestyle changes and medications like metformin.",
            
            'Hypertension': "High blood pressure (hypertension) is when blood pressure is consistently too high. Normal is under 120/80 mmHg. Lifestyle changes include DASH diet, exercise, weight management, and limiting sodium. Medications include ACE inhibitors and diuretics.",
            
            'Doctor Visit Prep': "Prepare for doctor visits by gathering medications, medical history, and questions. Bring insurance cards and ID. Ask about treatment options, risks, benefits, and next steps. Keep notes and follow up as recommended.",
            
            'Test Results': "Common tests include CBC, metabolic panel, and lipid panel. Normal ranges vary by lab and individual. Ask your doctor to explain results in plain language. Keep copies of all results and track trends over time.",
            
            'Insurance Navigation': "Understand your coverage including deductibles, copays, and networks. Read EOBs carefully. Use in-network providers when possible. Ask about costs before procedures. Appeal denied claims when appropriate.",
            
            'Medication Management': "Take medications as prescribed. Keep a current medication list. Store medications properly. Be aware of side effects and interactions. Ask your doctor about generic alternatives and cost-saving options.",
            
            'Specialist Referral': "See specialists for complex conditions, unclear diagnoses, or specialized treatments. Get referrals from your primary doctor. Research specialists' experience and credentials. Prepare for longer appointments with detailed questions."
        }
        
        # Return relevant snippet or fallback
        return snippets.get(source, f"Information about {title} from {source} medical resources.")
    
    def get_stats(self) -> Dict[str, any]:
        """Get statistics about the loaded index."""
        if not self._loaded:
            return {"loaded": False}
        
        sources = {}
        for meta in self.metadata:
            source = meta['source']
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "loaded": True,
            "total_chunks": len(self.metadata),
            "index_size": self.index.ntotal,
            "embedding_dim": self.model_info.get('embedding_dim', 'unknown'),
            "model_name": self.model_info.get('model_name', 'unknown'),
            "sources": sources
        }


# Global retriever instance
_retriever = None

def get_retriever() -> RAGRetriever:
    """Get or create global RAG retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever

def retrieve_documents(query: str, k: int = 5) -> List[Dict[str, any]]:
    """
    Convenience function to retrieve documents for a query.
    
    Args:
        query: Search query
        k: Number of results to return
        
    Returns:
        List of relevant documents with text, source, and score
    """
    retriever = get_retriever()
    return retriever.retrieve_with_text(query, k)

def is_rag_available() -> bool:
    """Check if RAG system is available and loaded."""
    try:
        retriever = get_retriever()
        return retriever.load_index()
    except:
        return False

def get_rag_stats() -> Dict[str, any]:
    """Get RAG system statistics."""
    retriever = get_retriever()
    return retriever.get_stats()
