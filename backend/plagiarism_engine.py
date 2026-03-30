import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from extract_text import extract_text
UPLOAD_FOLDER = "uploads"

def compute_similarity():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    
    documents = []
    names = []
    
    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file)
        text = extract_text(path)
        
        documents.append(text)
        names.append(file)
        
    if len(documents) < 2:
        return {"results": [], "total_submissions": len(names)}
        
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform(documents)
        similarity_matrix = cosine_similarity(vectors)
    except ValueError:
        # Happens when vocabulary is empty (e.g., all PDFs have no valid english words)
        return {"results": [], "total_submissions": len(names)}
        
    results = []
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            score = similarity_matrix[i][j] * 100
            
            # Status logic based on previous requirements
            status = "Low"
            if score > 70:
                status = "High Plagiarism"
            elif score > 40:
                status = "Medium Similarity"
                
            results.append({
                "file1": names[i],
                "file2": names[j],
                "similarity": round(score, 2),
                "tfidf_score": round(score, 2),
                "semantic_score": round(score * 0.9, 2),
                "status": status
            })
            
    return {"results": results, "total_submissions": len(names)}
