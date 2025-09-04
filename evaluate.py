import os
import json
import argparse
from typing import List, Dict, Any

# Import the parsing function from your other script
# This requires both .py files to be in the same directory
try:
    from parse_tax_forms import find_tax_forms_in_pdf
except ImportError:
    print("Error: Make sure 'parse_tax_forms.py' is in the same directory.")
    exit(1)

def calculate_metrics_for_file(predicted: List[Dict], ground_truth: List[Dict]) -> Dict[str, int]:
    """
    Compares predicted form data against ground truth for a single file.

    Args:
        predicted: The list of form dictionaries returned by the parser.
        ground_truth: The list of form dictionaries from the ground-truth JSON.

    Returns:
        A dictionary containing the counts of true positives, false positives,
        and false negatives for this file.
    """
    # To compare lists of dictionaries, we convert them into a hashable format (sets of tuples).
    # This allows for efficient set-based comparisons. We sort the items in each
    # dictionary to ensure a canonical representation.
    predicted_set = {tuple(sorted(p.items())) for p in predicted}
    truth_set = {tuple(sorted(t.items())) for t in ground_truth}

    true_positives = len(predicted_set.intersection(truth_set))
    false_positives = len(predicted_set.difference(truth_set))
    false_negatives = len(truth_set.difference(predicted_set))

    return {
        "tp": true_positives,
        "fp": false_positives,
        "fn": false_negatives
    }

def evaluate_parser_accuracy(pdf_dir: str, ground_truth_dir: str) -> Dict[str, Any]:
    """
    Calculates precision, recall, and F1-score for the parser over a dataset.

    Args:
        pdf_dir: Path to the directory containing input PDF files.
        ground_truth_dir: Path to the directory containing ground-truth JSON files.

    Returns:
        A dictionary containing the overall metrics and per-file results.
    """
    total_tp, total_fp, total_fn = 0, 0, 0
    per_file_results = {}

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"Warning: No PDF files found in '{pdf_dir}'.")
        return {}
        
    print(f"Found {len(pdf_files)} PDF files to evaluate.")

    for pdf_filename in pdf_files:
        basename = os.path.splitext(pdf_filename)[0]
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        json_path = os.path.join(ground_truth_dir, f"{basename}.json")

        if not os.path.exists(json_path):
            print(f"Warning: No matching ground truth for '{pdf_filename}'. Skipping.")
            continue

        # 1. Get predictions from your parser
        predicted_forms = find_tax_forms_in_pdf(pdf_path)
        # 2. Filter labels which are not in the /target
        # These are the specific document types we would like to check.
        desired_forms = {
            "f1040s1", "f1040s3", "f1040sa", 
            "f1040sb", "f1040sc", "f1040sd", "f1040se", 
            "1040f", "f8889", "f8949"
        }
        predicted_forms_filtered = [
            form for form in predicted_forms 
            if form["document_type"] in desired_forms
        ]

        # 3. Load ground truth
        with open(json_path, 'r') as f:
            ground_truth_forms = json.load(f)

        # 4. Calculate metrics for the current file
        file_metrics = calculate_metrics_for_file(predicted_forms_filtered, 
                                                  ground_truth_forms)
        per_file_results[pdf_filename] = file_metrics
        
        # 5. Add to totals
        total_tp += file_metrics['tp']
        total_fp += file_metrics['fp']
        total_fn += file_metrics['fn']

    # Calculate overall metrics (micro-averaging)
    # Handle division by zero for precision, recall, and f1
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    overall_metrics = {
        "total_true_positives": total_tp,
        "total_false_positives": total_fp,
        "total_false_negatives": total_fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4)
    }

    return {
        "overall_metrics": overall_metrics,
        "per_file_results": per_file_results
    }

def main():
    """
    Main function to run the evaluation script from the command line.
    """
    parser = argparse.ArgumentParser(description="Evaluate the accuracy of the tax form parser.")
    parser.add_argument("pdf_dir", help="Directory containing the input PDF files.")
    parser.add_argument("ground_truth_dir", help="Directory containing the ground-truth JSON files.")
    args = parser.parse_args()

    results = evaluate_parser_accuracy(args.pdf_dir, args.ground_truth_dir)

    if results:
        print("\n--- Evaluation Results ---")
        print(json.dumps(results, indent=4))
        print("------------------------")

if __name__ == "__main__":
    main()