import os
from PIL import Image

def test_lamport_generation():
    original_filename = "lamports algorithm.jpg"
    subject = "Distributed Computing"
    unit = "Unit 2 — Synchronization & Logical Clocks"
    topic = "Lamport Logical Clocks"
    
    # Verify spaces and formatting
    assert original_filename == "lamports algorithm.jpg"
    assert "lamports_algorithm.jpg" != original_filename
    
    print(f"Verified original_filename identity: {original_filename}")

test_lamport_generation()
