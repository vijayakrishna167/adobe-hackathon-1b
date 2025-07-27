# **Project 1B: Persona-Driven Document Intelligence**

## **Adobe India Hackathon 2025: Connecting the Dots**

This project is a solution for Round 1B of the Adobe India Hackathon. It's an intelligent system that analyzes a collection of PDF documents and extracts the most relevant sections based on a specific user persona and their "job-to-be-done."

### **1\. Problem Statement**

The challenge is to build an offline, CPU-based system that can process 3-10 related PDF documents for a given user context. The system must identify and rank the most important sections and subsections from the document collection that are relevant to the user's role and task, producing a structured JSON output.

This requires moving beyond simple keyword matching to a deeper semantic understanding of both the user's intent and the document content.

### **2\. Our Approach**

Our solution tackles this challenge using a modern, efficient, and entirely offline approach centered around **Semantic Search** powered by a sentence-transformer model.

The core workflow is as follows:

1. **Contextual Query Formulation**: We begin by combining the user's persona and job\_to\_be\_done into a single, rich query string. This string represents the user's core intent.  
2. **Intelligent Text Extraction**: For each PDF, we don't just extract raw text. We parse the document structure to identify potential **headings** and the content that falls under them. Our heuristics for identifying headings are based on font properties (size and weight), which allows us to segment the documents logically, mirroring how a human would perceive them.  
3. **Semantic Embedding**: This is the heart of our solution. We use the all-MiniLM-L6-v2 sentence-transformer model to convert text into numerical vectors (embeddings).  
   * The contextual query is converted into a query vector.  
   * The title of every extracted section is converted into a vector.  
   * The content of each section is also processed for subsection analysis.  
4. **Relevance Ranking**: We use **Cosine Similarity** to calculate the semantic distance between the query vector and every section title vector. A higher similarity score means the section title is more semantically related to the user's goal. This allows us to rank the sections by their relevance, not just by keywords.  
5. **Subsection Analysis**: For the top-ranked sections, we perform a deeper analysis. We break the section's content into individual sentences, embed them, and again use cosine similarity against the original query vector. This allows us to extract and present the most potent and relevant sentences from a larger block of text, providing a concise and targeted summary.  
6. **Offline-First Design**: The entire process is designed to run offline. The sentence-transformer model is cached locally after the first run. By explicitly setting local\_files\_only=True during model loading, we ensure the solution makes no network calls during execution, strictly adhering to the competition rules.

### **3\. Libraries and Models Used**

* **sentence-transformers**: The core library for accessing and using the all-MiniLM-L6-v2 model for generating high-quality text embeddings.  
* **PyMuPDF (fitz)**: A highly efficient and fast library for parsing PDF files, extracting text, and accessing font information.  
* **torch**: The underlying deep learning framework required by sentence-transformers.  
* **Model**: all-MiniLM-L6-v2. This model was chosen for its excellent balance of performance and size (\~80MB), making it ideal for the CPU-only, offline constraints of the challenge.

### **4\. How to Build and Run the Solution**

The project is designed to be run inside a Docker container as per the hackathon requirements.

#### **Prerequisites**

* Docker installed and running on your machine.

#### **Build the Docker Image**

Navigate to the project's root directory in your terminal and run the following command to build the image:

docker build \-t adobe-hackathon-solution .

#### **Run the Container**

Once the image is built, you can run the solution using the following command. This command mounts your local input directory into the container and mounts the container's output directory back to your local machine.

1. Place all your input PDFs and the challenge.json file in an input folder in the project root.  
2. Create an empty output folder in the project root.  
3. Run the container:

docker run \--rm \-v "$(pwd)/input:/app/input" \-v "$(pwd)/output:/app/output" adobe-hackathon-solution

The container will start, automatically run the run.py script, process the files from /app/input, and place the resulting challenge1b\_output.json file in /app/output, which will appear in your local output folder. The container will then stop.