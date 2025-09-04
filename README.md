# hw_taxdome
Solution for HW assignment from TaxDome

### Some observations based on data analysis
- The annotation is not fully accurate — certain forms from the list are missing (not reflected in the JSON files), as revealed by document analysis. Consequently, accuracy evaluation against these data would not provide a fully reliable picture of the solution’s performance. For the purposes of this test case, however, we will disregard this issue and assume the dataset accuracy to be 100%.
- The gold dataset contains forms that are not included in the list of extractable forms specified in the task. From a business logic perspective, the solution should ideally not be restricted to the predefined list alone. For establishing a baseline, however, we will limit consideration to the forms written in JON files and calculate metrics only with respect to those labels.
- The reporting documents are of high quality and do not require additional steps such as OCR. Parsing can therefore be performed using standard tools. For future cases involving documents that do require OCR, the solution should be extended to include this functionality.


## Solution

- Given the structured nature of the data, it is feasible to design a solution without resorting to machine learning models, relying instead on rule-based and heuristic methods. The limited amount of available data further restricts the possibility of training or fine-tuning ML models to an acceptable quality. A rules-based solution would provide fast inference performance but would require effort in collecting and formalizing the necessary form definitions.
- Based on document review, forms typically start on a new page. Form titles are positioned in the top-left corner of the page.

### Create environemnt, activate one and install requirements.txt
- python3.12 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

### Other prerequisites
- Place /input and /target folders with input dataset and expected outputs to /data

### Running service
- In order to parse tax forms from PDF file and output the results to console, run the following command: `python parse_tax_forms.py <path_to_your_pdf_file.pdf>`
- In order to calculate the metrics based on dataset in /data, run the following command: `python evaluate.py`.

#### Metrics
- The pipeline was designed to extract all possible forms written in ALL_FORM_PATTERNS variabel in `parse_tax_forms.py`. However, for the evaluation only the labels written in JSON files were taken into account:
```
desired_forms = {
            "f1040s1", "f1040s3", "f1040sa", 
            "f1040sb", "f1040sc", "f1040sd", "f1040se", 
            "1040f", "f8889", "f8949"
        }
```
- The metrics were generated using command `python evaluate.py data/input data/target`:
```
{
    "overall_metrics": {
        "total_true_positives": 55,
        "total_false_positives": 4,
        "total_false_negatives": 8,
        "precision": 0.9322,
        "recall": 0.873,
        "f1_score": 0.9016
    },
    "per_file_results": {
        "dummy4.pdf": {
            "tp": 4,
            "fp": 1,
            "fn": 1
        },
        "dummy5.pdf": {
            "tp": 6,
            "fp": 1,
            "fn": 2
        },
        "dummy7.pdf": {
            "tp": 6,
            "fp": 0,
            "fn": 0
        },
        "dummy6.pdf": {
            "tp": 4,
            "fp": 1,
            "fn": 1
        },
        "dummy2.pdf": {
            "tp": 8,
            "fp": 0,
            "fn": 1
        },
        "dummy3.pdf": {
            "tp": 6,
            "fp": 1,
            "fn": 2
        },
        "dummy1.pdf": {
            "tp": 7,
            "fp": 0,
            "fn": 1
        },
        "dummy10.pdf": {
            "tp": 6,
            "fp": 0,
            "fn": 0
        },
        "dummy8.pdf": {
            "tp": 7,
            "fp": 0,
            "fn": 0
        },
        "dummy9.pdf": {
            "tp": 1,
            "fp": 0,
            "fn": 0
        }
    }
}
```

#### AI assitance
- ChatGPT and AIStudio from Google were used to quickly check the possible packages to parse PDF files, with pros and cons for each package.
- Also, LLMs were used to define regex expressions based on list of expected forms.
- Evaluation script was generated with help from Gemini 2.5 Pro.
