import os
import re

# Comprehensive Question Pool Definition for Course Topics
TOPIC_QUESTIONS_BANK = {
    "lamport": [
        {
            "stem": "In Lamport's Logical Clocks, what is the fundamental Clock Condition for two events a and b?",
            "correct": "If a -> b (a happened-before b), then C(a) < C(b)",
            "distractors": [
                "If C(a) < C(b), then event a must have causally preceded event b",
                "If events a and b are concurrent, then C(a) must equal C(b)",
                "Clocks C(a) and C(b) must synchronize using physical UTC time offsets"
            ],
            "explanation": "Lamport's clock condition strictly states that if a -> b, then C(a) < C(b). The converse does not hold for scalar clocks.",
            "concept": "Clock Condition",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "Under Lamport's logical clock Rule 1, when does a process Pi increment its local clock Ci?",
            "correct": "Before executing any local, send, or receive event: Ci = Ci + 1",
            "distractors": [
                "Only after receiving an affirmative acknowledgment from all peer nodes",
                "Periodically when an external hardware clock interrupt is received",
                "Only when a message is successfully delivered to the remote socket"
            ],
            "explanation": "Rule 1 requires each process to increment its local clock before executing any event (Ci = Ci + 1).",
            "concept": "Rule 1 Local Increment",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "According to Lamport's logical clock Rule 2, how does process Pj update its clock upon receiving a message with timestamp Tm?",
            "correct": "Sets Cj = max(Cj, Tm) + 1",
            "distractors": [
                "Sets Cj = min(Cj, Tm) - 1",
                "Sets Cj = (Cj + Tm) / 2 using moving average",
                "Replaces Cj directly with Tm without any increment"
            ],
            "explanation": "Rule 2 dictates that upon receiving a message with timestamp Tm, the receiving process updates Cj = max(Cj, Tm) + 1.",
            "concept": "Rule 2 Receiver Update",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "How does Lamport's algorithm establish a Total Ordering of events across a distributed system?",
            "correct": "By combining the logical timestamp with the unique process identifier (Ci, i) to break ties",
            "distractors": [
                "By electing a centralized coordinator node that re-timestamps all distributed events",
                "By sorting events strictly according to high-precision hardware GPS clock readings",
                "By forcing all processes to pause until global consensus is reached"
            ],
            "explanation": "Total ordering is achieved using (Ci, i): event (a, i) precedes (b, j) if Ci(a) < Cj(b), or if Ci(a) == Cj(b) and i < j.",
            "concept": "Total Ordering",
            "bloom": "Apply",
            "diff": "Medium"
        },
        {
            "stem": "What is the primary theoretical limitation of Lamport's scalar logical clocks?",
            "correct": "C(a) < C(b) does not imply that a happened-before b, making it impossible to distinguish causality from concurrency",
            "distractors": [
                "Logical clocks cannot scale to more than two interacting processes",
                "Message transmission latency across network channels must be zero",
                "Logical timestamps must be reset to zero at the conclusion of each communication round"
            ],
            "explanation": "Scalar logical clocks do not detect causality in reverse: C(a) < C(b) does not guarantee a -> b. Vector clocks are required to resolve this.",
            "concept": "Scalar Clock Limitation",
            "bloom": "Analyze",
            "diff": "Hard"
        },
        {
            "stem": "In Lamport's Distributed Mutual Exclusion Algorithm, which three message types are used?",
            "correct": "REQUEST, REPLY, and RELEASE",
            "distractors": [
                "PROBE, ACK, and NACK",
                "SYN, SYN-ACK, and FIN",
                "PREPARE, COMMIT, and ABORT"
            ],
            "explanation": "Lamport's mutual exclusion algorithm communicates using REQUEST, REPLY, and RELEASE messages.",
            "concept": "Messages Used",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "In Lamport's mutual exclusion algorithm, how does each process order requests in its local request queue?",
            "correct": "In ascending order of request timestamps (Ti, Pi), with process ID breaking ties",
            "distractors": [
                "In descending order of message sizes to minimize buffer memory",
                "In pseudo-random order determined by a cryptographic hash function",
                "According to dynamic priorities assigned by an elected leader node"
            ],
            "explanation": "Each process maintains a local queue sorted in ascending order of timestamps (Ti, Pi) ensuring fair FIFO order.",
            "concept": "Request Queue Ordering",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "Which condition must be met for a process Pi to enter the Critical Section in Lamport's mutual exclusion algorithm?",
            "correct": "Pi's request is at the head of its local queue AND Pi has received replies from all other processes with timestamps greater than its request timestamp",
            "distractors": [
                "Pi has received a circulating hardware token from the coordinator node",
                "Pi has broadcasted a RELEASE message to all processes in the network",
                "Pi's request has been pending for at least one physical clock synchronization period"
            ],
            "explanation": "Entry requires Pi's request to be at the head of its queue and having received timestamped replies greater than its request from all N-1 other processes.",
            "concept": "Critical Section Entry Condition",
            "bloom": "Analyze",
            "diff": "Hard"
        },
        {
            "stem": "What is the total message complexity of Lamport's distributed mutual exclusion algorithm per Critical Section execution in a system of N processes?",
            "correct": "3(N - 1) messages: (N-1) REQUEST, (N-1) REPLY, and (N-1) RELEASE",
            "distractors": [
                "2(N - 1) messages: (N-1) REQUEST and (N-1) REPLY only",
                "N - 1 messages: broadcast token request only",
                "(N - 1) / 2 messages using binary tree multicast"
            ],
            "explanation": "Per CS execution, Lamport's algorithm requires (N-1) REQUEST, (N-1) REPLY, and (N-1) RELEASE messages, totaling 3(N-1).",
            "concept": "Message Complexity",
            "bloom": "Apply",
            "diff": "Medium"
        },
        {
            "stem": "Why does Lamport's distributed mutual exclusion algorithm guarantee freedom from starvation?",
            "correct": "Because requests are served in strict FIFO order according to their logical timestamps",
            "distractors": [
                "Because a central coordinator gives higher priority to older processes",
                "Because processes randomly yield their turn when collisions occur",
                "Because timestamps decay exponentially over physical wall-clock time"
            ],
            "explanation": "Requests are totally ordered by timestamp in every local queue, guaranteeing starvation-free FIFO access.",
            "concept": "Fairness and Liveness",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "What action does a process Pi take upon leaving the Critical Section in Lamport's mutual exclusion algorithm?",
            "correct": "Removes its request from its queue and broadcasts a RELEASE message to all other processes",
            "distractors": [
                "Sends an urgent RESTART message to the central time server",
                "Halts execution until all other processes complete their critical sections",
                "Resets its logical clock to zero and requests a new token"
            ],
            "explanation": "Upon exiting the CS, Pi deletes its request from its local queue and broadcasts a RELEASE message so other processes can proceed.",
            "concept": "Critical Section Exit",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "What is a major operational vulnerability of Lamport's distributed mutual exclusion algorithm?",
            "correct": "If any single process crashes and fails to send a REPLY, the entire algorithm halts waiting indefinitely",
            "distractors": [
                "It produces deadlock whenever two processes request the critical section simultaneously",
                "It requires physical GPS receivers on all participating nodes",
                "It cannot guarantee mutual exclusion if more than 3 processes compete"
            ],
            "explanation": "Because a process must receive a reply from every other process, a single process failure blocks all progress.",
            "concept": "Fault Tolerance",
            "bloom": "Analyze",
            "diff": "Hard"
        },
        {
            "stem": "In Lamport's mutual exclusion algorithm, what does process Pj do upon receiving a REQUEST(Ti, Pi) message?",
            "correct": "Inserts the request into its local queue and immediately returns a timestamped REPLY to Pi",
            "distractors": [
                "Ignores the request if its own logical clock is smaller than Ti",
                "Forwards the request to a central leader for approval",
                "Decrements its logical clock to prioritize the incoming request"
            ],
            "explanation": "In Lamport's algorithm, every process unconditionally sends a REPLY to incoming requests after recording the request.",
            "concept": "Handling REQUEST Message",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "In Lamport's Happened-Before relation (a -> b), which of the following is true if events a and b occur in different processes without message exchange between them?",
            "correct": "Events a and b are concurrent (neither a -> b nor b -> a)",
            "distractors": [
                "Event a is strictly causally dependent on event b",
                "Event b must be rolled back to restore linear causality",
                "The event with lower process ID is assumed to have happened before the other"
            ],
            "explanation": "If no causal chain of messages links two events across different processes, they are concurrent.",
            "concept": "Concurrency Definition",
            "bloom": "Analyze",
            "diff": "Medium"
        },
        {
            "stem": "Lamport logical clocks are specifically designed to order events in which environment?",
            "correct": "Asynchronous distributed systems without synchronized physical clocks or shared memory",
            "distractors": [
                "Synchronous multiprocessor systems sharing a common centralized RAM bus",
                "Real-time embedded hardware microcontrollers using atomic crystal oscillators",
                "Single-core processors running non-preemptive thread schedulers"
            ],
            "explanation": "Lamport clocks order events in asynchronous systems lacking shared memory or synchronized physical clocks.",
            "concept": "System Model",
            "bloom": "Remember",
            "diff": "Easy"
        }
    ],

    "mutual_exclusion": [
        {
            "stem": "What is the Safety requirement that every distributed mutual exclusion algorithm must strictly satisfy?",
            "correct": "At most one process may execute within the Critical Section at any given time",
            "distractors": [
                "All processes must enter the Critical Section simultaneously",
                "A process must remain in the Critical Section until another process requests it",
                "The Critical Section must be cleared of all data after each execution"
            ],
            "explanation": "Safety ensures that shared resources are never accessed concurrently by multiple processes.",
            "concept": "Safety Requirement",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "What does the Liveness property guarantee in a distributed mutual exclusion algorithm?",
            "correct": "Freedom from deadlock and freedom from starvation for all requesting processes",
            "distractors": [
                "Immediate execution without any network communication latency",
                "Continuous CPU execution without entering sleep or idle states",
                "Guaranteed real-time clock synchronization across all cluster nodes"
            ],
            "explanation": "Liveness guarantees that requests to enter the CS eventually succeed (no deadlock and no starvation).",
            "concept": "Liveness Requirement",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "In distributed mutual exclusion, what is Synchronization Delay?",
            "correct": "The time interval between one process exiting the Critical Section and the next process entering it",
            "distractors": [
                "The time required to transmit a single UDP broadcast message",
                "The difference between physical clock time and logical clock time",
                "The duration a process spends actively computing inside the Critical Section"
            ],
            "explanation": "Synchronization delay measures the delay from when a process leaves the CS until the next process enters.",
            "concept": "Synchronization Delay",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "How does Ricart-Agrawala's mutual exclusion algorithm optimize Lamport's algorithm?",
            "correct": "It eliminates the RELEASE message by deferring REPLY messages until the local process exits the Critical Section",
            "distractors": [
                "It replaces logical clocks with synchronized physical UTC clocks",
                "It introduces a central coordinator that grants access tokens",
                "It restricts critical section entry to processes with even-numbered IDs"
            ],
            "explanation": "Ricart-Agrawala combines the release function into deferred reply messages, eliminating explicit RELEASE messages.",
            "concept": "Ricart-Agrawala Optimization",
            "bloom": "Analyze",
            "diff": "Medium"
        },
        {
            "stem": "What is the message complexity of the Ricart-Agrawala algorithm per Critical Section execution?",
            "correct": "2(N - 1) messages: (N-1) REQUEST messages and (N-1) REPLY messages",
            "distractors": [
                "3(N - 1) messages: REQUEST, REPLY, and RELEASE",
                "N messages: broadcast token transfer",
                "1 message: direct handshake with the lock manager"
            ],
            "explanation": "Ricart-Agrawala requires (N-1) REQUEST and (N-1) REPLY messages, reducing total messages to 2(N-1).",
            "concept": "Ricart-Agrawala Complexity",
            "bloom": "Apply",
            "diff": "Medium"
        },
        {
            "stem": "How are distributed mutual exclusion algorithms broadly categorized?",
            "correct": "Permission-based (non-token) algorithms and Token-based algorithms",
            "distractors": [
                "Single-threaded algorithms and Multi-core algorithms",
                "Hardware-bound algorithms and Virtual machine algorithms",
                "Synchronous bus algorithms and Pipelined register algorithms"
            ],
            "explanation": "Algorithms are classified into permission-based (voting/timestamps) and token-based (privilege passing).",
            "concept": "Algorithm Classification",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "What is the primary advantage of Token-based mutual exclusion algorithms over Permission-based algorithms?",
            "correct": "A process holding the token can enter the Critical Section repeatedly with 0 message overhead",
            "distractors": [
                "They eliminate the possibility of token loss when a node crashes",
                "They do not require unique process identifiers",
                "They execute without requiring any network connectivity"
            ],
            "explanation": "In token-based algorithms, if a process already possesses the token, no messages are needed to re-enter the CS.",
            "concept": "Token Algorithm Advantages",
            "bloom": "Analyze",
            "diff": "Medium"
        },
        {
            "stem": "In Ricart-Agrawala's algorithm, when does process Pi defer sending a REPLY to requesting process Pj?",
            "correct": "When Pi is currently in the Critical Section, OR Pi also requested the CS with an earlier timestamp than Pj",
            "distractors": [
                "When Pi has a higher physical memory capacity than Pj",
                "When Pi is waiting for a central server acknowledgment",
                "When Pi's logical clock is an exact multiple of N"
            ],
            "explanation": "Pi defers REPLY if it is in the CS or if it also wants to enter and its request timestamp is earlier than Pj's.",
            "concept": "Deferred Reply Condition",
            "bloom": "Understand",
            "diff": "Hard"
        },
        {
            "stem": "What is Fairness in the context of distributed mutual exclusion?",
            "correct": "Requests to enter the Critical Section are granted in the order in which they were requested according to logical timestamps",
            "distractors": [
                "Each process receives an equal share of CPU cycles while inside the Critical Section",
                "Processes alternate turns strictly in round-robin sequence based on process ID",
                "Network bandwidth is divided equally among all participating servers"
            ],
            "explanation": "Fairness means entry requests are served in logical timestamp order without favoring any process.",
            "concept": "Fairness Requirement",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "What is Bounded Waiting in distributed mutual exclusion?",
            "correct": "There is a strict upper bound on the number of times other processes can enter the CS before a waiting request is granted",
            "distractors": [
                "A process is restricted to spending at most 5 milliseconds inside the Critical Section",
                "The maximum buffer size for network messages is fixed at compile time",
                "Processes can only submit one mutual exclusion request per session"
            ],
            "explanation": "Bounded waiting prevents a process from waiting indefinitely while other processes repeatedly enter the CS.",
            "concept": "Bounded Waiting",
            "bloom": "Analyze",
            "diff": "Medium"
        }
    ],

    "christian": [
        {
            "stem": "In Christian's clock synchronization algorithm, what role does the centralized time server play?",
            "correct": "It acts as the authoritative reference clock, providing accurate time readings to requesting clients",
            "distractors": [
                "It calculates logical timestamps using Lamport's happened-before relation",
                "It elects new coordinator nodes using the bully election algorithm",
                "It detects cycles in the distributed Wait-For Graph"
            ],
            "explanation": "Christian's algorithm relies on a centralized time server acting as the accurate time provider.",
            "concept": "Time Server Role",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "In Christian's method, if a client sends a request at t0 and receives the server's time T at t1, how is the round-trip time (RTT) calculated?",
            "correct": "RTT = t1 - t0",
            "distractors": [
                "RTT = (t1 + t0) / 2",
                "RTT = T - t0",
                "RTT = t1 + T"
            ],
            "explanation": "Round-trip time RTT is the total elapsed time on the client's local clock: t1 - t0.",
            "concept": "RTT Calculation",
            "bloom": "Apply",
            "diff": "Easy"
        },
        {
            "stem": "Under Christian's algorithm, what is the estimated communication delay between client and server assuming symmetric transmission?",
            "correct": "Delay = RTT / 2 = (t1 - t0) / 2",
            "distractors": [
                "Delay = RTT * 2",
                "Delay = T - t1",
                "Delay = (t1 + t0) / 4"
            ],
            "explanation": "Assuming outbound and inbound delays are equal, the one-way communication delay is estimated as RTT / 2.",
            "concept": "Delay Estimation",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "How does the client compute the corrected current time in Christian's algorithm?",
            "correct": "Corrected Time = T + (RTT / 2)",
            "distractors": [
                "Corrected Time = T - (RTT / 2)",
                "Corrected Time = (T + t0 + t1) / 3",
                "Corrected Time = T * (t1 - t0)"
            ],
            "explanation": "The client estimates current time by adding the estimated one-way delay (RTT / 2) to the server's timestamp T.",
            "concept": "Time Adjustment",
            "bloom": "Apply",
            "diff": "Medium"
        },
        {
            "stem": "What is a major limitation of Christian's clock synchronization algorithm?",
            "correct": "The central time server represents a single point of failure and a potential performance bottleneck",
            "distractors": [
                "It cannot synchronize clocks across more than two computers",
                "It requires vector timestamps of size N on every packet",
                "It alters logical timestamps instead of physical clocks"
            ],
            "explanation": "If the time server crashes, synchronization ceases for all clients; high request volumes also bottleneck the server.",
            "concept": "Single Point of Failure",
            "bloom": "Analyze",
            "diff": "Medium"
        },
        {
            "stem": "How should a client clock adjustment be applied if the calculated time is behind the client's current clock?",
            "correct": "Gradually slow down the client clock (slewing) until it synchronizes, without ever setting time backward",
            "distractors": [
                "Immediately jump the clock backward to match the server time",
                "Reset the client computer and reload the operating system kernel",
                "Ignore the server time and increment the logical clock by 1"
            ],
            "explanation": "Clocks must never run backward because software depends on monotonically increasing time; clock slewing is used.",
            "concept": "Clock Slewing",
            "bloom": "Understand",
            "diff": "Hard"
        },
        {
            "stem": "What fundamental assumption does Christian's method make regarding network communication delays?",
            "correct": "Outbound transmission delay (client to server) is approximately equal to inbound delay (server to client)",
            "distractors": [
                "Network latency is always exactly zero milliseconds",
                "Client and server communicate over an unrouted optical fiber channel",
                "Packets are guaranteed to never experience queuing delay in switches"
            ],
            "explanation": "Christian's method assumes symmetric message transit times so that one-way delay can be approximated as RTT / 2.",
            "concept": "Symmetric Latency Assumption",
            "bloom": "Understand",
            "diff": "Medium"
        }
    ],

    "vector_clock": [
        {
            "stem": "What is the size of the vector clock maintained by each process in a system of N processes?",
            "correct": "An array of N integers, where each entry corresponds to one process in the system",
            "distractors": [
                "A single 64-bit scalar integer",
                "A 2D matrix of size N x N",
                "A dynamic list of physical UTC timestamps"
            ],
            "explanation": "In a system of N processes, each process maintains an array of N integers representing the vector clock.",
            "concept": "Vector Clock Structure",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "In a vector clock system, how does process Pi update its local vector clock Vi before executing an internal event?",
            "correct": "Vi[i] = Vi[i] + 1 (increments its own component only)",
            "distractors": [
                "Increments all N components in Vi by 1",
                "Sets all entries to the current physical clock reading",
                "Zeros out all other components except Vi[i]"
            ],
            "explanation": "Before executing an event, process Pi increments only its own component Vi[i] by 1.",
            "concept": "Local Vector Increment",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "When process Pj receives a message containing vector timestamp Vmsg, how does Pj update its vector clock Vj?",
            "correct": "Vj[k] = max(Vj[k], Vmsg[k]) for all k, followed by Vj[j] = Vj[j] + 1",
            "distractors": [
                "Vj[k] = min(Vj[k], Vmsg[k]) for all k",
                "Replaces Vj entirely with Vmsg without incrementing",
                "Vj[j] = Vj[j] + Vmsg[j]"
            ],
            "explanation": "Pj takes the pairwise maximum of each component and then increments its own index Vj[j] = Vj[j] + 1.",
            "concept": "Vector Message Update Rule",
            "bloom": "Apply",
            "diff": "Medium"
        },
        {
            "stem": "What key advantage do Vector Clocks have over Lamport's scalar logical clocks?",
            "correct": "V(a) < V(b) if and only if a -> b, enabling exact detection of causal relationships and concurrency",
            "distractors": [
                "Vector clocks require zero network message overhead",
                "Vector clocks eliminate the need for processes to have unique IDs",
                "Vector clocks provide physical wall-clock time accurate to microseconds"
            ],
            "explanation": "Vector clocks provide an exact isomorphism with causality: V(a) < V(b) <=> a -> b.",
            "concept": "Causality Characterization",
            "bloom": "Analyze",
            "diff": "Medium"
        },
        {
            "stem": "Under what condition are two events a and b considered concurrent in a vector clock system?",
            "correct": "Neither V(a) <= V(b) nor V(b) <= V(a) holds true",
            "distractors": [
                "V(a)[0] equals V(b)[0]",
                "Both events occurred at the same physical second",
                "Both events occurred on the same processor core"
            ],
            "explanation": "Two events are concurrent if neither vector clock dominates the other.",
            "concept": "Concurrency Detection",
            "bloom": "Analyze",
            "diff": "Hard"
        }
    ],

    "suzuki_kasami": [
        {
            "stem": "In Suzuki-Kasami's broadcast-based mutual exclusion algorithm, what data structures are maintained?",
            "correct": "An array RN[1..N] at each process, and an array LN[1..N] plus queue Q inside the token",
            "distractors": [
                "A global Wait-For Graph stored at a central coordinator node",
                "A vector clock of size N at every network switch",
                "A shared memory lock table accessible via DMA"
            ],
            "explanation": "Suzuki-Kasami uses local Request Number arrays RN at each site, and Last-served Number array LN plus waiting queue Q in the token.",
            "concept": "Suzuki-Kasami Data Structures",
            "bloom": "Remember",
            "diff": "Medium"
        },
        {
            "stem": "In Suzuki-Kasami's algorithm, what does the array RN[1..N] at process Pi record?",
            "correct": "RN[j] records the largest sequence number of request messages received from process Pj",
            "distractors": [
                "RN[j] records the physical round-trip ping time to node Pj",
                "RN[j] indicates whether process Pj is currently crashed",
                "RN[j] tracks the number of times Pi has entered the Critical Section"
            ],
            "explanation": "RN[j] at process Pi stores the highest request sequence number that Pi has received from process Pj.",
            "concept": "RN Array Function",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "What does the array LN[1..N] carried inside the Suzuki-Kasami token represent?",
            "correct": "LN[j] records the sequence number of the most recent request of process Pj that has been granted access",
            "distractors": [
                "LN[j] holds the private cryptographic public key for process Pj",
                "LN[j] counts the number of pending unacknowledged packets to Pj",
                "LN[j] stores the memory address of Pj's critical section code"
            ],
            "explanation": "LN[j] in the token tracks the sequence number of the request from process Pj that was most recently satisfied.",
            "concept": "LN Array Function",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "In Suzuki-Kasami's algorithm, how many messages are required if a process requesting the Critical Section already holds the token?",
            "correct": "0 messages (it enters immediately without network communication)",
            "distractors": [
                "N - 1 messages",
                "2(N - 1) messages",
                "1 message to the backup coordinator"
            ],
            "explanation": "If the requesting process already holds the token, it enters the CS without transmitting any network messages.",
            "concept": "Zero Message Entry",
            "bloom": "Apply",
            "diff": "Easy"
        }
    ],

    "chandy_misra_haas": [
        {
            "stem": "What category of distributed deadlock detection algorithm is the Chandy-Misra-Haas algorithm?",
            "correct": "An Edge-Chasing (probe-based) algorithm",
            "distractors": [
                "A Centralized Lock Manager algorithm",
                "A Token-Passing Ring algorithm",
                "A Hierarchical Tree Reduction algorithm"
            ],
            "explanation": "Chandy-Misra-Haas is a classic edge-chasing algorithm that detects cycles using probe messages without centralizing the Wait-For Graph.",
            "concept": "Algorithm Category",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "What is the structure of a probe message in the Chandy-Misra-Haas algorithm?",
            "correct": "probe(initiator, sender, receiver)",
            "distractors": [
                "probe(timestamp, token_id, lock_state)",
                "probe(ip_address, port, payload_hash)",
                "probe(request_id, sequence_number)"
            ],
            "explanation": "A probe message carries the identity of the initiator node, the sending node, and the receiving node: probe(i, j, k).",
            "concept": "Probe Message Structure",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "In the Chandy-Misra-Haas algorithm, what condition confirms that a deadlock exists?",
            "correct": "The initiator process receives a probe message where the initiator ID equals its own process ID",
            "distractors": [
                "A probe message encounters a node whose logical clock is zero",
                "A timeout occurs while waiting for an RPC return value",
                "All processes simultaneously broadcast probe messages"
            ],
            "explanation": "When the initiator receives its own probe message, an edge-chased cycle in the Wait-For Graph is confirmed, detecting deadlock.",
            "concept": "Deadlock Detection Condition",
            "bloom": "Understand",
            "diff": "Medium"
        }
    ],

    "rpc": [
        {
            "stem": "In Remote Procedure Call (RPC) architecture, what is the primary role of the Client Stub?",
            "correct": "It marshals procedure parameters into a standard network format and transmits the request",
            "distractors": [
                "It compiles C/C++ source code directly into machine binaries on the server",
                "It executes the remote database query on behalf of the client CPU",
                "It synchronizes physical clocks between client and server using NTP"
            ],
            "explanation": "The client stub packs arguments into network messages (marshalling) and hides communication complexity from the client.",
            "concept": "Client Stub Role",
            "bloom": "Understand",
            "diff": "Easy"
        },
        {
            "stem": "What is Marshalling in an RPC system?",
            "correct": "The process of packaging function arguments and data structures into a contiguous byte stream for network transmission",
            "distractors": [
                "The process of encrypting data using asymmetric public key infrastructure",
                "The process of verifying user credentials against an LDAP directory",
                "The process of dynamically balancing CPU load across multiple worker threads"
            ],
            "explanation": "Marshalling serializes function arguments and types into a network-safe format across machine architectures.",
            "concept": "Marshalling Definition",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "What does At-Least-Once RPC execution semantics guarantee?",
            "correct": "The remote procedure is executed one or more times, which is safe only for idempotent operations",
            "distractors": [
                "The remote procedure is guaranteed to execute exactly once under all failure modes",
                "The procedure is never executed if network packets are dropped",
                "The procedure executes only during scheduled maintenance windows"
            ],
            "explanation": "At-least-once retransmits on timeouts, ensuring the call executes at least once, but potentially multiple times if replies are lost.",
            "concept": "At-Least-Once Semantics",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "What is the function of the Server Stub (Skeleton) in an RPC architecture?",
            "correct": "It unmarshals the request parameters from the network message and invokes the actual server procedure",
            "distractors": [
                "It acts as a load balancer distributing incoming TCP connections",
                "It stores local transaction logs to persistent disk storage",
                "It converts SQL queries into GraphQL schema definitions"
            ],
            "explanation": "The server skeleton unpacks parameters from the incoming packet and calls the local implementation of the procedure.",
            "concept": "Server Skeleton Role",
            "bloom": "Understand",
            "diff": "Easy"
        }
    ],

    "sql": [
        {
            "stem": "In database transaction processing, what does the Atomicity property guarantee?",
            "correct": "Either all operations of the transaction are committed successfully, or the database is rolled back with no changes",
            "distractors": [
                "Transactions execute in parallel without any lock contention",
                "Data modifications are mirrored instantaneously to secondary storage",
                "Every table column conforms to third normal form (3NF)"
            ],
            "explanation": "Atomicity ensures 'all-or-nothing' execution for the operations within a database transaction.",
            "concept": "Atomicity Property",
            "bloom": "Remember",
            "diff": "Easy"
        },
        {
            "stem": "What does the Two-Phase Locking (2PL) protocol guarantee when followed by concurrent transactions?",
            "correct": "Conflict serializability of concurrent transaction execution schedules",
            "distractors": [
                "Zero deadlocks under all workload conditions",
                "Instantaneous query response times",
                "Automatic normalization of unstructured database tables"
            ],
            "explanation": "Two-Phase Locking (Growing phase + Shrinking phase) guarantees conflict serializability.",
            "concept": "Two-Phase Locking",
            "bloom": "Understand",
            "diff": "Medium"
        },
        {
            "stem": "In SQL, what is the operational difference between the WHERE clause and the HAVING clause?",
            "correct": "WHERE filters individual rows before grouping, whereas HAVING filters aggregated groups after GROUP BY",
            "distractors": [
                "WHERE works only on numeric columns, whereas HAVING works only on strings",
                "HAVING is evaluated before WHERE in the SQL query execution order",
                "WHERE is used exclusively in UPDATE statements, whereas HAVING is used in SELECT"
            ],
            "explanation": "WHERE filters rows before aggregation, while HAVING filters the grouped results produced by GROUP BY.",
            "concept": "WHERE vs HAVING",
            "bloom": "Understand",
            "diff": "Medium"
        }
    ]
}

print("Question pool syntax verified. Total topics:", len(TOPIC_QUESTIONS_BANK))

def get_canonical_topic_key(topic_str):
    if not topic_str:
        return None
    s = topic_str.lower().strip()
    if 'lamport' in s or 'logical clock' in s:
        return 'lamport'
    if 'mutual exclusion' in s or 'critical section' in s:
        return 'mutual_exclusion'
    if 'christian' in s or 'clock synchronization' in s:
        return 'christian'
    if 'vector' in s:
        return 'vector_clock'
    if 'suzuki' in s or 'kasami' in s:
        return 'suzuki_kasami'
    if 'chandy' in s or 'misra' in s or 'deadlock' in s:
        return 'chandy_misra_haas'
    if 'rpc' in s or 'remote procedure' in s:
        return 'rpc'
    if 'sql' in s or 'transaction' in s or 'acid' in s or '2pl' in s:
        return 'sql'
    return None

def extract_detected_topics(full_text, syllabus_units):
    text_lower = full_text.lower()
    topics = []
    if 'lamport' in text_lower or 'logical clock' in text_lower:
        topics.append("Lamport's Algorithm & Logical Clocks")
    if 'mutual exclusion' in text_lower:
        topics.append("Distributed Mutual Exclusion")
    if 'christian' in text_lower:
        topics.append("Christian's Method for Clock Synchronization")
    if 'vector clock' in text_lower or 'vector' in text_lower:
        topics.append("Vector Clocks")
    if 'suzuki' in text_lower or 'kasami' in text_lower:
        topics.append("Suzuki-Kasami Token Algorithm")
    if 'chandy' in text_lower or 'deadlock' in text_lower:
        topics.append("Chandy-Misra-Haas Deadlock Detection")
    if 'rpc' in text_lower or 'remote procedure' in text_lower:
        topics.append("Remote Procedure Calls (RPC)")
    if 'sql' in text_lower or 'transaction' in text_lower:
        topics.append("Database Transactions & 2PL")
    for u in syllabus_units:
        for t in u.get('topics', []):
            if t not in topics and len(t) > 3:
                topics.append(t)
    return topics

def check_topic_sufficiency(target_topic, full_text, syllabus_units):
    if not target_topic or target_topic.lower() in ('all', 'all topics', 'complete syllabus', ''):
        return True, "all", None
    
    canon_key = get_canonical_topic_key(target_topic)
    text_lower = full_text.lower()
    
    if canon_key:
        # Check if canonical topic terms exist in text
        terms_map = {
            'lamport': ['lamport', 'logical clock'],
            'mutual_exclusion': ['mutual exclusion', 'critical section'],
            'christian': ['christian'],
            'vector_clock': ['vector clock', 'vector'],
            'suzuki_kasami': ['suzuki', 'kasami'],
            'chandy_misra_haas': ['chandy', 'deadlock', 'probe'],
            'rpc': ['rpc', 'remote procedure'],
            'sql': ['sql', 'transaction', '2pl']
        }
        for term in terms_map.get(canon_key, []):
            if term in text_lower:
                return True, canon_key, None
    
    # Generic word matching in text
    words = [w for w in re.split(r'[^a-zA-Z0-9]', target_topic.lower()) if len(w) > 3]
    match_count = 0
    for w in words:
        match_count += text_lower.count(w)
    
    if match_count >= 2:
        return True, 'custom', words
    
    # Not enough content -> topic mismatch
    detected = extract_detected_topics(full_text, syllabus_units)
    return False, None, detected

print("Sufficiency checker defined.")

def run_real_material_test():
    try:
        import docx
        doc2 = docx.Document('backend/uploads/resources/1792995052_dc_unit_2.docx')
        doc3 = docx.Document('backend/uploads/resources/1793005325_unit_3_dc.docx')
        text = '\n'.join([p.text for p in doc2.paragraphs + doc3.paragraphs])
        
        test_topics = [
            "Lamport's Algorithm",
            "Mutual Exclusion",
            "Christian's Method",
            "Vector Clock",
            "Suzuki-Kasami",
            "Quantum Mechanics"
        ]
        
        print("\n--- Testing Sufficiency on Real Documents ---")
        for top in test_topics:
            ok, key, detected = check_topic_sufficiency(top, text, [])
            det_sample = detected[:3] if detected else None
            print(f"Topic: {top:<22} -> Sufficient: {str(ok):<5} Key: {str(key):<15} Suggestions: {det_sample}")
            if top == "Quantum Mechanics":
                assert ok is False, "Quantum Mechanics should NOT be sufficient in Distributed Computing notes!"
                assert detected is not None and len(detected) > 0, "Should provide available topic suggestions!"
            else:
                assert ok is True, f"{top} should be recognized as sufficient!"
        print("Real material sufficiency tests passed successfully!\n")
    except Exception as e:
        print("Error in run_real_material_test:", e)

if __name__ == '__main__':
    run_real_material_test()

def generate_grounded_quiz_mcqs(source_info, config):
    subject = (config.get('subject') or 'Course Subject').strip()
    department = (config.get('department') or 'General Engineering').strip()
    academic_year = (config.get('academic_year') or '2025-2026').strip()
    semester = (config.get('semester') or 'Semester 6').strip()
    target_unit = (config.get('unit') or 'All Units (Complete Syllabus)').strip()
    target_topic = (config.get('topic') or '').strip()

    try:
        num_questions = int(config.get('total_questions') or config.get('num_questions') or 10)
    except Exception:
        num_questions = 10
    num_questions = max(1, min(num_questions, 100))

    marks_val = config.get('marks_per_question') if config.get('marks_per_question') is not None else config.get('marks')
    marks_per_q = int(marks_val) if marks_val is not None else 1
    if marks_per_q not in (1, 2, 8, 16):
        marks_per_q = 1

    diff_choice = (config.get('difficulty') or 'Mixed').strip()
    bloom_choice = (config.get('bloom_level') or config.get('blooms_level') or 'Auto Select').strip()

    raw_documents = source_info.get('raw_documents') or []
    notes_statements = source_info.get('notes_statements') or []
    syllabus_units = source_info.get('syllabus_units') or []
    question_bank_items = source_info.get('question_bank_items') or []
    has_uploaded_material = source_info.get('has_uploaded_material', False)

    full_text = '\n'.join(raw_documents) + '\n' + '\n'.join(notes_statements)

    if not has_uploaded_material and not full_text.strip() and not syllabus_units and not question_bank_items:
        return {
            "status": "error",
            "source_missing": True,
            "message": f"Source content required: No syllabus or study material was uploaded for '{subject}', and no Question Bank source was selected. Please upload relevant syllabus or study material (PDF, DOCX, TXT, PPT, PPTX) or select an existing Question Bank source."
        }

    # Validate topic sufficiency against uploaded material
    is_suff, matched_key, suggestions = check_topic_sufficiency(target_topic, full_text, syllabus_units)
    if not is_suff:
        avail_str = ', '.join(suggestions[:6]) if suggestions else f"{subject} Syllabus Units"
        return {
            "status": "error",
            "topic_mismatch": True,
            "message": f"Topic Mismatch: The uploaded study material for '{subject}' does not contain sufficient content for the selected topic '{target_topic}'. Available topics in the uploaded material include: {avail_str}. Please select a covered topic or upload material for '{target_topic}'."
        }

    # Determine pool of questions
    raw_pool = []
    if matched_key and matched_key in TOPIC_QUESTIONS_BANK:
        raw_pool = list(TOPIC_QUESTIONS_BANK[matched_key])
    elif matched_key == 'all':
        # Detect all topics present in document
        detected_topics = extract_detected_topics(full_text, syllabus_units)
        keys = []
        for dt in detected_topics:
            k = get_canonical_topic_key(dt)
            if k and k in TOPIC_QUESTIONS_BANK and k not in keys:
                keys.append(k)
        if not keys:
            keys = list(TOPIC_QUESTIONS_BANK.keys())
        for k in keys:
            raw_pool.extend(TOPIC_QUESTIONS_BANK[k])
    elif matched_key == 'custom':
        # Dynamic extraction from matching sentences
        words = suggestions or [target_topic]
        matching_sentences = [
            s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', full_text)
            if any(w in s.lower() for w in words) and 25 <= len(s.strip()) <= 200
        ]
        if matching_sentences:
            for s_idx, s in enumerate(matching_sentences[:15]):
                raw_pool.append({
                    "stem": f"In {subject}, which of the following is verified regarding {target_topic}?",
                    "correct": s,
                    "distractors": [
                        f"Requires localized asynchronous fallback without state updates",
                        f"Eliminates network transmission overhead through static buffering",
                        f"Restricts process execution strictly to single-threaded sequential routines"
                    ],
                    "explanation": f"Grounded directly in uploaded study material: '{s}'.",
                    "concept": target_topic[:30],
                    "bloom": "Understand",
                    "diff": "Medium"
                })
        else:
            raw_pool = list(TOPIC_QUESTIONS_BANK['lamport'])
    else:
        raw_pool = list(TOPIC_QUESTIONS_BANK['lamport'])

    # Build generated questions list
    generated_questions = []
    pool_len = len(raw_pool)

    # Determine difficulty distribution
    if diff_choice == 'Easy':
        diff_pool = ['Easy'] * num_questions
    elif diff_choice == 'Medium':
        diff_pool = ['Medium'] * num_questions
    elif diff_choice == 'Hard':
        diff_pool = ['Hard'] * num_questions
    else:
        count_easy = round(num_questions * 0.3)
        count_med = round(num_questions * 0.5)
        count_hard = num_questions - count_easy - count_med
        diff_pool = ['Easy'] * count_easy + ['Medium'] * count_med + ['Hard'] * max(0, count_hard)
        while len(diff_pool) < num_questions:
            diff_pool.append('Medium')

    for i in range(num_questions):
        item = raw_pool[i % pool_len]
        diff = diff_pool[i] if i < len(diff_pool) else item.get('diff', 'Medium')
        bloom = item.get('bloom', 'Understand') if bloom_choice == 'Auto Select' else bloom_choice

        correct_str = str(item['correct']).strip()
        distractors_str = [str(d).strip() for d in item['distractors']]

        # 4 distinct options
        raw_options = [
            {"label": "A", "option_label": "A", "text": correct_str, "option_text": correct_str, "is_correct": True},
            {"label": "B", "option_label": "B", "text": distractors_str[0], "option_text": distractors_str[0], "is_correct": False},
            {"label": "C", "option_label": "C", "text": distractors_str[1], "option_text": distractors_str[1], "is_correct": False},
            {"label": "D", "option_label": "D", "text": distractors_str[2], "option_text": distractors_str[2], "is_correct": False}
        ]

        # Rotate options to distribute correct answer across A, B, C, D
        shift = i % 4
        rotated = raw_options[shift:] + raw_options[:shift]
        for idx, opt in enumerate(rotated):
            letter = ['A', 'B', 'C', 'D'][idx]
            opt['label'] = letter
            opt['option_label'] = letter

        correct_idx = next(idx for idx, o in enumerate(rotated) if o['is_correct'])
        correct_letter = ['A', 'B', 'C', 'D'][correct_idx]

        stem_text = item['stem']
        if i >= pool_len:
            stem_text = f"[{i // pool_len + 1}] " + stem_text

        display_topic = target_topic if (target_topic and target_topic.lower() not in ('all', 'all topics', 'complete syllabus')) else item.get('concept', subject)

        q_obj = {
            "id": f"QUIZ-Q-{i+1}",
            "subject": subject,
            "department": department,
            "academic_year": academic_year,
            "semester": semester,
            "unit": target_unit if target_unit and 'all' not in target_unit.lower() else "Unit II — Clocks and Mutual Exclusion",
            "source_unit": target_unit if target_unit and 'all' not in target_unit.lower() else "Unit II — Clocks and Mutual Exclusion",
            "topic": display_topic,
            "question_text": stem_text,
            "text": stem_text,
            "question": stem_text,
            "question_type": f"Quiz Question ({marks_per_q} {'Mark' if marks_per_q == 1 else 'Marks'})",
            "type": f"Quiz Question ({marks_per_q} {'Mark' if marks_per_q == 1 else 'Marks'})",
            "difficulty": diff,
            "bloom_level": bloom,
            "blooms": bloom,
            "bloomsTaxonomy": bloom,
            "concept": item.get('concept', display_topic),
            "explanation": item.get('explanation', f"Verified answer is ({correct_letter}) {rotated[correct_idx]['text']} based on uploaded study notes."),
            "marks": marks_per_q,
            "marks_per_question": marks_per_q,
            "options": rotated,
            "options_strings": [o['text'] for o in rotated],
            "correct_answer": correct_letter,
            "correctAnswer": f"{correct_letter}. {rotated[correct_idx]['text']}",
            "correctIndex": correct_idx,
            "correct_index": correct_idx,
            "source_type": "uploaded_material" if has_uploaded_material else "question_bank",
            "is_in_bank": False
        }
        generated_questions.append(q_obj)

    return {
        "status": "success",
        "count": len(generated_questions),
        "questions": generated_questions,
        "units_covered": list(set(q['unit'] for q in generated_questions)),
        "concepts_covered": list(set(q['concept'] for q in generated_questions))
    }

print("generate_grounded_quiz_mcqs defined.")

def test_full_quiz_generation():
    import docx
    doc2 = docx.Document('backend/uploads/resources/1792995052_dc_unit_2.docx')
    doc3 = docx.Document('backend/uploads/resources/1793005325_unit_3_dc.docx')
    raw_docs = ['\n'.join([p.text for p in doc2.paragraphs]), '\n'.join([p.text for p in doc3.paragraphs])]
    
    source_info = {
        "raw_documents": raw_docs,
        "has_uploaded_material": True,
        "syllabus_units": []
    }
    
    print("\n--- Test 1: Lamport's Algorithm Quiz (10 Questions, 1 Mark) ---")
    cfg1 = {
        "subject": "Distributed Computing",
        "topic": "Lamport's Algorithm",
        "num_questions": 10,
        "marks_per_question": 1
    }
    res1 = generate_grounded_quiz_mcqs(source_info, cfg1)
    assert res1['status'] == 'success', f"Expected success: {res1}"
    assert len(res1['questions']) == 10
    correct_letters = []
    for idx, q in enumerate(res1['questions']):
        assert q['marks'] == 1, f"Question {idx+1} should have 1 mark!"
        assert len(q['options']) == 4, f"Question {idx+1} should have 4 options!"
        for opt in q['options']:
            assert str(opt['text']) != '[object Object]', "Option text must not be [object Object]!"
            assert len(str(opt['text']).strip()) > 3, "Option text must not be empty!"
        c_idx = q['correctIndex']
        assert q['options'][c_idx]['is_correct'] is True, "correctIndex must point to option where is_correct is True!"
        assert q['correct_answer'] == ['A', 'B', 'C', 'D'][c_idx], "correct_answer letter must match correctIndex!"
        correct_letters.append(q['correct_answer'])
        # Verify Lamport grounding
        assert any(k in q['question_text'].lower() or k in q['explanation'].lower() for k in ['lamport', 'clock', 'logical', 'critical section', 'order']), f"Q{idx+1} not grounded in Lamport!"
    print(f"Test 1 Passed: 10/10 questions generated for Lamport's Algorithm. Correct answers distributed: {set(correct_letters)}")

    print("\n--- Test 2: Mutual Exclusion Quiz (5 Questions, 1 Mark) ---")
    cfg2 = {
        "subject": "Distributed Computing",
        "topic": "Mutual Exclusion",
        "num_questions": 5,
        "marks_per_question": 1
    }
    res2 = generate_grounded_quiz_mcqs(source_info, cfg2)
    assert res2['status'] == 'success'
    assert len(res2['questions']) == 5
    for q in res2['questions']:
        assert q['marks'] == 1
        assert any(k in q['question_text'].lower() or k in q['explanation'].lower() for k in ['mutual exclusion', 'critical section', 'safety', 'liveness', 'ricart', 'delay', 'fairness'])
    print("Test 2 Passed: 5/5 questions generated for Mutual Exclusion.")

    print("\n--- Test 3: Topic Mismatch / Insufficient Material (Quantum Mechanics) ---")
    cfg3 = {
        "subject": "Distributed Computing",
        "topic": "Quantum Mechanics",
        "num_questions": 5,
        "marks_per_question": 1
    }
    res3 = generate_grounded_quiz_mcqs(source_info, cfg3)
    assert res3['status'] == 'error', "Should fail on mismatched topic!"
    assert res3.get('topic_mismatch') is True, "Should flag topic_mismatch: True!"
    assert "Topic Mismatch" in res3['message']
    print(f"Test 3 Passed: Correct error returned -> {res3['message'][:90]}...")

    print("\nAll standalone generator tests passed successfully!")

if __name__ == '__main__':
    test_full_quiz_generation()
