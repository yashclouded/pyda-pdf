# PDF Question Extractor for JEE Papers

This tool extracts questions, answers, and images from JEE Mains and Advanced previous year question paper PDFs, organizing them into structured JSON files with associated images.

## Features

- Extracts questions, options, answers, and solutions from PDFs
- Captures and organizes images associated with questions and answers
- Creates a JSON file with all structured data
- Organizes output into a clean folder structure
- Processes multiple PDFs in batch


## Usage

1. Place your JEE question paper PDFs in a folder named `qns-pdf` in the same directory as the script
2. Run the script:


This will process all PDFs in the `qns-pdf` folder and create an `extracted_questions` folder with the results.

### Custom Folders

You can specify custom input and output folders:

```bash
python pdf_extractor.py /path/to/pdf/folder /path/to/output/folder
```

## Output Structure

For each PDF, the program creates:

```
extracted_questions/
  ├── pdf_name_1/
  │   ├── questions.json
  │   └── images/
  │       ├── q1_img1.png
  │       ├── q1_ans_img1.png
  │       └── ...
  ├── pdf_name_2/
  │   └── ...
  └── ...
```

The `questions.json` file contains structured data like:

```json
[
  {
    "id": 1,
    "question_text": "Full question text here...",
    "options": [
      {"option": "A", "text": "Option A text"},
      {"option": "B", "text": "Option B text"},
      {"option": "C", "text": "Option C text"},
      {"option": "D", "text": "Option D text"}
    ],
    "answer": "C",
    "solution": "Full solution explanation...",
    "question_images": [
      {"image_id": 1, "page_number": 1, "image_path": "images/q1_img1.png"}
    ],
    "answer_images": [
      {"image_id": 2, "page_number": 1, "image_path": "images/q1_ans_img1.png"}
    ]
  },
  // More questions...
]
```

## Customization

The script includes pattern matching optimized for JEE question papers, but you can modify the regular expressions in the code to better match your specific PDF formats if needed.

## Troubleshooting

If you encounter issues with extraction:

1. Make sure your PDFs are text-searchable (not just scanned images)
2. Check if the PDFs follow standard JEE question formatting
3. Try adjusting the regex patterns in the code to match your specific format