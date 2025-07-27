# **Technical Approach: Persona-Driven Document Intelligence**

Our solution for Project 1B is built on the principle of **semantic understanding**, moving beyond simple keywords to grasp the true intent behind a user's query and the meaning within the documents. The entire system is designed to be efficient, robust, and fully compliant with the offline, CPU-only constraints of the challenge.

### **Core Technology: Sentence-Transformers**

The cornerstone of our approach is the all-MiniLM-L6-v2 sentence-transformer model. We chose this model for three key reasons:

1. **High Performance:** It offers a state-of-the-art balance between speed and semantic accuracy, making it ideal for understanding nuanced relationships between text.  
2. **Compact Size:** At approximately 80MB, it easily fits within the 1GB model size constraint.  
3. **Offline Capability:** The model can be cached locally, and by using the local\_files\_only=True flag during initialization, we guarantee the final solution makes no network calls.

### **Intelligent Content Parsing**

We recognized that raw text extraction is insufficient. To accurately identify the most important sections, we first needed to understand the document's structure. Our extract\_structured\_chunks function uses heuristics based on font size and weight (bolding) from the PyMuPDF library to distinguish headings from body text. This allows us to segment the documents into logical sections, mirroring how a human would read them. This structural analysis is more resilient than methods that rely only on text patterns.

### **Two-Tiered Relevance Ranking**

Our ranking system operates in two stages for maximum precision:

1. **Section Ranking:** We first rank the relevance of **section titles**. The user's persona and job-to-be-done are combined into a single query vector. We then calculate the cosine similarity between this query vector and the vector for each section title. This quickly identifies the most relevant high-level topics within the document collection.  
2. **Subsection Analysis:** For the top-ranked sections, we perform a more granular analysis. The full text content of the section is broken down into individual sentences. Each sentence is then vectorized and compared against the original query vector. The most similar sentences are extracted to form the refined\_text. This two-step process ensures that the final output is not only relevant at a topic level but also provides the most potent, concise information from within those topics.

By combining intelligent document parsing with a two-tiered semantic search, our solution effectively connects the user's specific needs to the most relevant information scattered across multiple documents, delivering a precise and actionable result.