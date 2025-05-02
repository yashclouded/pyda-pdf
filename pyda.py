import os
import json
import re
import shutil
from pathlib import Path
from pdf_extract_kit import PDFExtractor, PDFExtractorConfig
from pdf_extract_kit.elements import TextElement, ImageElement

def extract_questions_answers(pdf_path):
    """
    Extract questions, answers and images from a PDF file.
    Returns a list of dictionaries containing question data.
    """
    # Configure the extractor
    config = PDFExtractorConfig(
        extract_images=True,
        group_lines=True,
        detect_titles=True,
        detect_lists=True
    )
    
    extractor = PDFExtractor(config)
    elements = extractor.extract(pdf_path)
    
    questions = []
    current_question = None
    question_number = 0
    
    # Patterns for JEE questions and answers
    question_pattern = re.compile(r'^Q\.?\s*(\d+)\.?\s*', re.IGNORECASE)
    answer_pattern = re.compile(r'^(Answer|Ans|Solution)[\s:]', re.IGNORECASE)
    option_pattern = re.compile(r'^\s*\(?([A-D])\)?\s*', re.IGNORECASE)
    
    # Process elements
    for i, elem in enumerate(elements):
        if isinstance(elem, TextElement):
            text = elem.text.strip()
            
            # Check if this is a new question
            question_match = question_pattern.match(text)
            if question_match:
                # Save previous question if exists
                if current_question:
                    questions.append(current_question)
                
                # Extract question number
                question_number = int(question_match.group(1))
                
                # Initialize new question
                current_question = {
                    "id": question_number,
                    "question_text": text[question_match.end():].strip(),
                    "options": [],
                    "answer": None,
                    "solution": None,
                    "question_images": [],
                    "answer_images": []
                }
            
            # Check if this is an option
            elif current_question and option_pattern.match(text):
                option_match = option_pattern.match(text)
                option_letter = option_match.group(1).upper()
                option_text = text[option_match.end():].strip()
                current_question["options"].append({
                    "option": option_letter,
                    "text": option_text
                })
            
            # Check if this is the answer or solution
            elif current_question and answer_pattern.match(text):
                solution_text = text[answer_pattern.match(text).end():].strip()
                
                # If solution is just the letter, it's likely just the answer
                if len(solution_text) <= 2 and re.match(r'^[A-D]$', solution_text):
                    current_question["answer"] = solution_text
                else:
                    # Check if there's an answer embedded at the start
                    answer_in_solution = re.match(r'^[A-D][\.\)]?\s*', solution_text)
                    if answer_in_solution:
                        current_question["answer"] = solution_text[0]
                        current_question["solution"] = solution_text[answer_in_solution.end():].strip()
                    else:
                        current_question["solution"] = solution_text
            
            # Continue building the current question text
            elif current_question and not current_question["answer"]:
                current_question["question_text"] += " " + text
        
        # Handle images
        elif isinstance(elem, ImageElement) and current_question:
            image_data = {
                "image_id": len(current_question["question_images"]) + len(current_question["answer_images"]) + 1,
                "page_number": elem.page_number,
                "image_path": elem.image_path
            }
            
            # Determine if image belongs to question or answer based on position
            if current_question["answer"] is None:
                current_question["question_images"].append(image_data)
            else:
                current_question["answer_images"].append(image_data)
    
    # Add the last question
    if current_question:
        questions.append(current_question)
    
    return questions

def process_pdf_folder(input_folder, output_folder):
    """
    Process all PDFs in the input folder and save extracted data to output folder.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        
        # Create a folder for this PDF
        pdf_name = os.path.splitext(pdf_file)[0]
        pdf_output_folder = os.path.join(output_folder, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)
        
        # Create images folder
        images_folder = os.path.join(pdf_output_folder, "images")
        os.makedirs(images_folder, exist_ok=True)
        
        try:
            # Extract questions, answers, and images
            questions = extract_questions_answers(pdf_path)
            
            # Update image paths and copy images to output folder
            for question in questions:
                # Process question images
                for img in question["question_images"]:
                    original_path = img["image_path"]
                    new_filename = f"q{question['id']}_img{img['image_id']}.png"
                    new_path = os.path.join(images_folder, new_filename)
                    
                    # Copy image file
                    shutil.copy2(original_path, new_path)
                    
                    # Update path in the data
                    img["image_path"] = os.path.join("images", new_filename)
                
                # Process answer images
                for img in question["answer_images"]:
                    original_path = img["image_path"]
                    new_filename = f"q{question['id']}_ans_img{img['image_id']}.png"
                    new_path = os.path.join(images_folder, new_filename)
                    
                    # Copy image file
                    shutil.copy2(original_path, new_path)
                    
                    # Update path in the data
                    img["image_path"] = os.path.join("images", new_filename)
            
            # Save data to JSON file
            json_path = os.path.join(pdf_output_folder, "questions.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            print(f"Processed {pdf_file}: Extracted {len(questions)} questions")
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    # Default folders
    input_folder = "qns-pdf"
    output_folder = "extracted_questions"
    
    # Allow command-line arguments to override defaults
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    # Process all PDFs in the input folder
    process_pdf_folder(input_folder, output_folder)
    print(f"All PDFs processed. Results saved to {output_folder}")