"""
HC First-Gen Navigator - Document Loader for RAG (Local Embeddings)
Loads HC Catalog and Student Handbook into Supabase with local embeddings
Uses sentence-transformers - no API calls, completely free
"""

import os
import requests
from io import BytesIO
import PyPDF2
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cpgbvsfepbwfjplyxcdm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNwZ2J2c2ZlcGJ3ZmpwbHl4Y2RtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjIxOTIxMiwiZXhwIjoyMDkxNzk1MjEyfQ.aj4BjrnTmmmD6YQYMoWnBKLQUCt05XleSKegpW15G1I")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize embedding model (will download on first run, ~90MB)
print("Loading embedding model (first run downloads ~90MB)...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!\n")

# HC Documents to download
HC_DOCUMENTS = [
    {
        "url": "https://www.hcfl.edu/sites/default/files/docs/2025-08/HCCFL_25-26_StudentHandbook_.pdf",
        "source": "HC Student Handbook 2025-2026",
        "type": "pdf"
    }
]

def download_pdf(url):
    """Download PDF from URL"""
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        total_pages = len(reader.pages)
        print(f"Extracting text from {total_pages} pages...")
        
        for page_num, page in enumerate(reader.pages):
            if page_num % 10 == 0:
                print(f"  Page {page_num + 1}/{total_pages}...", end="\r")
            page_text = page.extract_text()
            if page_text:
                text += f"\n{page_text}"
        
        print(f"\nExtracted {len(text)} characters")
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def chunk_text(text, chunk_size=800, overlap=100):
    """Break text into overlapping chunks"""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.strip()) > 100:
            chunks.append(chunk.strip())
    
    return chunks

def create_embedding(text):
    """Create embedding using local sentence-transformers model"""
    try:
        # Model outputs 384 dimensions, we need to pad to 1024
        embedding_384 = model.encode(text, convert_to_numpy=True)
        
        # Pad with zeros to reach 1024 dimensions
        import numpy as np
        embedding_1024 = np.pad(embedding_384, (0, 1024 - 384), mode='constant')
        
        return embedding_1024.tolist()
    except Exception as e:
        print(f"\nError creating embedding: {e}")
        return None

def upload_to_supabase(source, chunks):
    """Upload chunks to Supabase with embeddings"""
    print(f"\nCreating embeddings and uploading {len(chunks)} chunks...")
    print("This may take a few minutes...")
    successful = 0
    
    for i, chunk in enumerate(chunks):
        if (i + 1) % 5 == 0 or i == 0:
            print(f"  Chunk {i+1}/{len(chunks)} ({successful} uploaded)", end="\r")
        
        # Create embedding
        embedding = create_embedding(chunk)
        if embedding is None:
            print(f"\nSkipping chunk {i+1} - embedding failed")
            continue
        
        # Insert into Supabase
        data = {
            "source": source,
            "section": f"Chunk {i+1}",
            "content": chunk,
            "embedding": embedding
        }
        
        try:
            supabase.table("hc_documents").insert(data).execute()
            successful += 1
        except Exception as e:
            print(f"\nError inserting chunk {i+1}: {e}")
    
    print(f"\n\nCompleted {source}")
    print(f"Successfully uploaded: {successful}/{len(chunks)} chunks")
    return successful

def main():
    print("=" * 70)
    print("HC First-Gen Navigator - Document Loader (Local Embeddings)")
    print("=" * 70)
    
    total_uploaded = 0
    
    # Process each document
    for doc in HC_DOCUMENTS:
        print(f"\n{'='*70}")
        print(f"Processing: {doc['source']}")
        print('='*70)
        
        try:
            # Download PDF
            pdf_file = download_pdf(doc['url'])
            if pdf_file is None:
                continue
            
            # Extract text
            text = extract_text_from_pdf(pdf_file)
            if text is None or len(text) < 100:
                print("Insufficient text extracted, skipping...")
                continue
            
            # Chunk text
            chunks = chunk_text(text)
            print(f"Created {len(chunks)} chunks")
            
            # Upload to Supabase with embeddings
            uploaded = upload_to_supabase(doc['source'], chunks)
            total_uploaded += uploaded
            
        except Exception as e:
            print(f"Error processing {doc['source']}: {e}")
    
    print("\n" + "=" * 70)
    print(f"COMPLETE! Total chunks uploaded: {total_uploaded}")
    print(f"Check your Supabase hc_documents table to verify")
    print("=" * 70)

if __name__ == "__main__":
    main()