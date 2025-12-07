# Sub-Agents Test Cases

Test prompts for validating all RAG sub-agents. Each section targets specific agent capabilities.

---

## 1. Curriculum Agent (`rag_curriculum_agent`)

**Purpose:** Maps program structure, corpus IDs, course navigation

### TC-CUR-01: Course Overview
```
What is the course outline for this program?
```

### TC-CUR-02: Chapter Order
```
What chapters are available and in what order should I study them?
```

### TC-CUR-03: Prerequisites Check
```
What are the prerequisites for chapter 5?
```

### TC-CUR-04: Learning Outcomes
```
What are the learning outcomes for this course?
```

### TC-CUR-05: Corpus Identification
```
Which corpus contains information about machine learning fundamentals?
```

### TC-CUR-06: Chapter Navigation
```
Which chapter should I start with as a beginner?
```

### TC-CUR-07: Specific Corpus Query
```
Search in corpus ID "abc123" for information about data structures.
```

---

## 2. Learning Agent (`rag_learning_agent`)

**Purpose:** Topic explanations, examples, concept comparisons

### TC-LRN-01: Concept Explanation
```
What's the difference between generic software products and customized software
products?
```


## 3. Assessment Agent (`rag_assessment_agent`)

**Purpose:** Rubrics, grading, feedback on submissions

### TC-ASS-02: Grade Submission
```
Evaluate the following student submission according to the rubric criterion 'Apply
relevant software engineering principles in Assessment 3.
Determine the correct performance level (NN /PA/ CR / DI / HD) and explain your
reasoning based on the rubric.
Student submission:
My system will use a microservices architecture because it is modern and popular. Each
service will be developed separately so that the team can work in parallel. This
architecture ensures good performance and will make deployment easier. The
requirements are simple: users should be able to log in, add products to cart, and make
payments. We will design the database later after the implementation is done. I did not
create any UML models because they take too long and are not always needed in real
projects
```

---

## 4. Progress Agent (`rag_progress_agent`)

**Purpose:** Track chapter completion, recommend next steps

### TC-PRG-01: Report Completion
```
I finished chapter 1 and chapter 2.
```

### TC-PRG-02: What's Next
```
What's next for me to study?
```

### TC-PRG-03: Progress Snapshot
```
Show me my current progress.
```

### TC-PRG-04: Course Outline Request
```
Show me the complete course outline with all chapters.
```

### TC-PRG-05: Multiple Chapters Completed
```
I've completed chapters 1, 2, 3, and 5. What should I do next?
```
