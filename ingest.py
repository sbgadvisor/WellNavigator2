#!/usr/bin/env python3
"""
Document ingestion script for WellNavigator RAG system.
Loads markdown files from /data/corpus/, chunks them, embeds them, and stores in FAISS index.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ Missing dependencies. Install with: pip install faiss-cpu sentence-transformers")
    exit(1)


class DocumentIngester:
    """Handles document loading, chunking, embedding, and indexing."""
    
    def __init__(self, corpus_dir: str = "data/corpus", index_dir: str = "data/index"):
        self.corpus_dir = Path(corpus_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model (lightweight, good for health content)
        print("🔄 Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Storage for documents and embeddings
        self.documents = []
        self.embeddings = []
        self.metadata = []
    
    def load_documents(self) -> List[Dict[str, str]]:
        """Load all markdown files from corpus directory."""
        print(f"📂 Loading documents from {self.corpus_dir}")
        
        documents = []
        for md_file in self.corpus_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from first heading or filename
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else md_file.stem.replace('-', ' ').title()
                
                # Clean filename for source label
                source = md_file.stem.replace('-', ' ').title()
                
                documents.append({
                    'filename': md_file.name,
                    'title': title,
                    'content': content,
                    'source': source
                })
                
                print(f"  ✅ Loaded: {md_file.name} ({len(content)} chars)")
                
            except Exception as e:
                print(f"  ❌ Error loading {md_file.name}: {e}")
        
        print(f"📄 Loaded {len(documents)} documents")
        return documents
    
    def chunk_document(self, content: str, source: str, title: str) -> List[Dict[str, str]]:
        """Split document into overlapping chunks for better retrieval."""
        chunks = []
        
        # Split by headers and paragraphs
        sections = re.split(r'\n(#{1,6} .+)', content)
        
        current_section = ""
        current_title = title
        
        for i, section in enumerate(sections):
            if section.startswith('#'):
                # Save previous section if it has content
                if current_section.strip():
                    chunks.extend(self._split_large_section(current_section, current_title, source))
                
                # Start new section
                current_section = section + "\n"
                current_title = section.lstrip('# ').strip()
            else:
                current_section += section
        
        # Handle last section
        if current_section.strip():
            chunks.extend(self._split_large_section(current_section, current_title, source))
        
        return chunks
    
    def _split_large_section(self, content: str, section_title: str, source: str) -> List[Dict[str, str]]:
        """Split large sections into smaller chunks with overlap."""
        # Target chunk size (characters)
        target_size = 800
        overlap = 100
        
        if len(content) <= target_size:
            return [{
                'text': content.strip(),
                'title': section_title,
                'source': source
            }]
        
        chunks = []
        start = 0
        
        while start < len(content):
            # Find good break point (end of sentence or paragraph)
            end = start + target_size
            
            if end >= len(content):
                end = len(content)
            else:
                # Look for good break points
                for break_char in ['\n\n', '. ', '! ', '? ', '\n']:
                    break_pos = content.rfind(break_char, start, end)
                    if break_pos > start + target_size // 2:  # Don't make chunks too small
                        end = break_pos + len(break_char)
                        break
            
            chunk_text = content[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'title': section_title,
                    'source': source
                })
            
            # Move start with overlap
            start = max(start + 1, end - overlap)
        
        return chunks
    
    def embed_chunks(self, chunks: List[Dict[str, str]]) -> Tuple[np.ndarray, List[Dict]]:
        """Create embeddings for document chunks."""
        print(f"🔄 Creating embeddings for {len(chunks)} chunks...")
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        # Prepare metadata
        metadata = []
        for i, chunk in enumerate(chunks):
            metadata.append({
                'id': i,
                'title': chunk['title'],
                'source': chunk['source'],
                'text_length': len(chunk['text']),
                'chunk_index': i
            })
        
        return embeddings, metadata
    
    def build_index(self, embeddings: np.ndarray, metadata: List[Dict]) -> faiss.Index:
        """Build FAISS index from embeddings."""
        print("🔄 Building FAISS index...")
        
        # Create FAISS index (L2 distance for semantic similarity)
        index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        print(f"✅ Built index with {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.Index, metadata: List[Dict]):
        """Save FAISS index and metadata to disk."""
        print("💾 Saving index and metadata...")
        
        # Save FAISS index
        faiss.write_index(index, str(self.index_dir / "faiss_index.bin"))
        
        # Save metadata
        with open(self.index_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Save embedding model info
        model_info = {
            'model_name': 'all-MiniLM-L6-v2',
            'embedding_dim': self.embedding_dim,
            'index_type': 'IndexFlatIP',
            'total_documents': len(metadata)
        }
        
        with open(self.index_dir / "model_info.json", 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2)
        
        print(f"✅ Saved index to {self.index_dir}")
    
    def ingest(self):
        """Main ingestion pipeline."""
        print("🚀 Starting document ingestion...")
        
        # Load documents
        documents = self.load_documents()
        if not documents:
            print("❌ No documents found to ingest")
            return
        
        # Process each document
        all_chunks = []
        for doc in documents:
            print(f"📝 Chunking: {doc['filename']}")
            chunks = self.chunk_document(doc['content'], doc['source'], doc['title'])
            all_chunks.extend(chunks)
            print(f"  Created {len(chunks)} chunks")
        
        print(f"📊 Total chunks: {len(all_chunks)}")
        
        # Create embeddings
        embeddings, metadata = self.embed_chunks(all_chunks)
        
        # Build and save index
        index = self.build_index(embeddings, metadata)
        self.save_index(index, metadata)
        
        # Print summary
        print("\n✅ Ingestion complete!")
        print(f"📄 Documents processed: {len(documents)}")
        print(f"📝 Total chunks: {len(all_chunks)}")
        print(f"🧮 Embedding dimension: {self.embedding_dim}")
        print(f"💾 Index saved to: {self.index_dir}")
        
        # Show chunk distribution
        sources = {}
        for chunk in all_chunks:
            source = chunk['source']
            sources[source] = sources.get(source, 0) + 1
        
        print("\n📊 Chunks by source:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count} chunks")


def main():
    """Run the ingestion process."""
    ingester = DocumentIngester()
    ingester.ingest()


if __name__ == "__main__":
    main()
