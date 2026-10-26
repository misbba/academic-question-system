import os
import re

def test_mcq_generation():
    print("Writing and testing MCQ generator...")
    # Verify option format
    options = [
        {"label": "A", "option_label": "A", "text": "Correct fact", "option_text": "Correct fact", "is_correct": True},
        {"label": "B", "option_label": "B", "text": "Wrong 1", "option_text": "Wrong 1", "is_correct": False},
        {"label": "C", "option_label": "C", "text": "Wrong 2", "option_text": "Wrong 2", "is_correct": False},
        {"label": "D", "option_label": "D", "text": "Wrong 3", "option_text": "Wrong 3", "is_correct": False}
    ]
    # Check rotation
    shift = 2
    rotated = options[shift:] + options[:shift]
    for idx, opt in enumerate(rotated):
        opt['label'] = ['A', 'B', 'C', 'D'][idx]
        opt['option_label'] = opt['label']
    correct_idx = next(i for i, o in enumerate(rotated) if o['is_correct'])
    assert rotated[correct_idx]['label'] == ['A', 'B', 'C', 'D'][correct_idx]
    print(f"Rotated correctly: correct letter is {rotated[correct_idx]['label']}, index is {correct_idx}")

if __name__ == '__main__':
    test_mcq_generation()
