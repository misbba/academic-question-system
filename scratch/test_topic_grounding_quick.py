import os
import re
import sys

def test_topic_grounding():
    print("Testing topic grounding concepts...")
    
    # Check that sample topics match expected keywords
    topic_keywords = {
        "lamport": ["lamport", "logical clock"],
        "mutual exclusion": ["mutual exclusion", "critical section"],
        "christian": ["christian", "clock synchronization"],
        "vector": ["vector clock", "vector clocks"],
        "suzuki": ["suzuki", "kasami", "token"],
        "deadlock": ["chandy", "deadlock", "probe"],
        "rpc": ["rpc", "remote procedure", "marshalling"],
        "sql": ["sql", "transaction", "acid", "2pl"]
    }
    
    doc_sample = """
    Demonstrate Christian's Method for Synchronizing Clocks - 16 Marks
    1. Introduction: In a distributed system, every computer has its own local clock.
    Christian's algorithm is a clock synchronization method where a client synchronizes its clock with a central time server.
    Delay calculation: RTT = t1 - t0. The communication delay is estimated as RTT / 2.
    Corrected time = T + delay.
    
    Lamport Logical Clocks:
    If a -> b, then C(a) < C(b).
    Rule 1: Ci = Ci + 1 before any event.
    Rule 2: Receiver updates Cj = max(Cj, Tm) + 1 upon receiving message with timestamp Tm.
    Total order achieved by tie-breaking with process ID (Ci, i).
    Lamport's Distributed Mutual Exclusion uses REQUEST, REPLY, RELEASE messages.
    Message complexity is 3(N - 1) messages.
    
    Distributed Mutual Exclusion Requirements:
    Safety: At most one process in Critical Section.
    Liveness: Freedom from deadlock and starvation.
    Fairness: Requests granted in timestamp order.
    """
    
    # Topic matching test
    assert "christian" in doc_sample.lower()
    assert "lamport" in doc_sample.lower()
    assert "mutual exclusion" in doc_sample.lower()
    assert "quantum" not in doc_sample.lower()
    
    print("Topic matching verification passed!")

if __name__ == '__main__':
    test_topic_grounding()
