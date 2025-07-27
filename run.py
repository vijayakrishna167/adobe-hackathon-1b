# run.py
import os
import json
import glob
from src.processing import process_documents_for_persona

# Define input and output directories
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

def main():
    # 1. Find the main input JSON file in the input directory
    # Using glob to find the first .json file, as the name might vary
    json_input_files = glob.glob(os.path.join(INPUT_DIR, '*.json'))
    if not json_input_files:
        print(f"Error: No input JSON file found in the '{INPUT_DIR}' directory.")
        return

    main_input_path = json_input_files[0]
    print(f"Reading challenge data from: {main_input_path}")

    with open(main_input_path, 'r') as f:
        challenge_data = json.load(f)

    # 2. Get the list of PDF filenames from the challenge data
    pdf_filenames = [doc['filename'] for doc in challenge_data['documents']]
    pdf_paths = [os.path.join(INPUT_DIR, fname) for fname in pdf_filenames]

    # 3. Process the documents based on the persona and job
    print(f"Processing {len(pdf_paths)} documents for persona: {challenge_data['persona']['role']}")
    result = process_documents_for_persona(pdf_paths, challenge_data)

    # 4. Write the final output JSON
    output_path = os.path.join(OUTPUT_DIR, 'challenge1b_output.json')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)
    
    print(f"Successfully created output at {output_path}")

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    main()