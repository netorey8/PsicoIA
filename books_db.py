import os
import re
import sys
import subprocess
import math

# Auto-install dependency for PDF reading
try:
    import pypdf
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        import pypdf
    except Exception as e:
        print(f"Error al instalar pypdf: {e}")

class BooksDB:
    def __init__(self, books_dir="books"):
        self.books_dir = books_dir
        self.documents = []  # List of dict: {"id": int, "book": str, "author": str, "text": str, "tokens": set}
        self.df = {}         # Document Frequency for terms
        self.num_docs = 0
        self.avg_doc_len = 0
        
        if not os.path.exists(self.books_dir):
            os.makedirs(self.books_dir)
            
        self.load_all_books()

    def clean_text(self, text):
        # Convert to lowercase and get words
        text = text.lower()
        words = re.findall(r'\b[a-záéíóúüñ]{3,}\b', text)
        return words

    def load_all_books(self):
        self.documents = []
        doc_id = 0
        total_len = 0
        
        if not os.path.exists(self.books_dir):
            return
            
        for fname in os.listdir(self.books_dir):
            path = os.path.join(self.books_dir, fname)
            if not os.path.isfile(path):
                continue
                
            # Parse Author and Title from filename (e.g., "Viktor Frankl - El hombre en busca de sentido.txt")
            parts = os.path.splitext(fname)[0].split(" - ")
            if len(parts) >= 2:
                author = parts[0].strip()
                title = parts[1].strip()
            else:
                author = "Autor Desconocido"
                title = os.path.splitext(fname)[0].strip()
                
            content = ""
            if fname.lower().endswith(".txt"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error leyendo txt {fname}: {e}")
            elif fname.lower().endswith(".pdf"):
                try:
                    reader = pypdf.PdfReader(path)
                    pages_text = []
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            pages_text.append(t)
                    content = "\n".join(pages_text)
                except Exception as e:
                    print(f"Error leyendo pdf {fname}: {e}")
                    
            if not content.strip():
                continue
                
            # Split into paragraphs/chunks of ~4-8 sentences
            paragraphs = re.split(r'\n\s*\n', content)
            for para in paragraphs:
                para = para.strip()
                # Clean up multiple whitespaces
                para = re.sub(r'\s+', ' ', para)
                if len(para) > 100:  # Ignore very short lines/headers
                    tokens = self.clean_text(para)
                    if tokens:
                        self.documents.append({
                            "id": doc_id,
                            "book": title,
                            "author": author,
                            "text": para,
                            "tokens": tokens,
                            "len": len(tokens)
                        })
                        total_len += len(tokens)
                        doc_id += 1
                        
        self.num_docs = len(self.documents)
        if self.num_docs > 0:
            self.avg_doc_len = total_len / self.num_docs
            self.calculate_df()
            
        print(f"Base de Datos cargada: {self.num_docs} fragmentos de libros indexados.")

    def calculate_df(self):
        self.df = {}
        for doc in self.documents:
            unique_terms = set(doc["tokens"])
            for term in unique_terms:
                self.df[term] = self.df.get(term, 0) + 1

    def search(self, query, limit=3):
        if not self.documents:
            return []
            
        query_tokens = self.clean_text(query)
        if not query_tokens:
            return []
            
        # Pure Python BM25 Scoring
        # Score(D, Q) = sum( IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * (|D| / avgDL))) )
        k1 = 1.5
        b = 0.75
        scores = []
        
        for doc in self.documents:
            score = 0.0
            doc_len = doc["len"]
            
            for token in query_tokens:
                if token not in self.df:
                    continue
                    
                # Term frequency in document
                tf = doc["tokens"].count(token)
                if tf == 0:
                    continue
                    
                # Calculate IDF
                # idf = log((N - n + 0.5) / (n + 0.5) + 1)
                n = self.df[token]
                idf = math.log((self.num_docs - n + 0.5) / (n + 0.5) + 1.0)
                
                # BM25 term
                denom = tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                term_score = idf * (tf * (k1 + 1.0)) / denom
                score += term_score
                
            if score > 0:
                scores.append((score, doc))
                
        # Sort by score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scores[:limit]:
            results.append({
                "book": doc["book"],
                "author": doc["author"],
                "text": doc["text"],
                "score": round(score, 2)
            })
        return results
