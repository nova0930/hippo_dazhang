# System Design

```mermaid
flowchart TD
    A[User bedtime story request] --> B[Request Analyzer]
    B --> C[Storyteller LLM]
    C --> D[LLM Judge]
    D --> E{Passes quality threshold?}
    E -- No --> F[Revision Prompt]
    F --> C
    E -- Yes --> G[Story Draft]
    G --> H[Ask User for Feedback]
    H --> I{User wants changes?}
    I -- Yes --> J[User Feedback Revision]
    J --> K[Final Story Text]
    I -- No --> K[Final Story Text]
    K --> L[Text-to-Speech]
    L --> M[MP3 Bedtime Story]
```

## Design Summary

The system separates story generation into planning, storytelling, judging, and revision.  
The request analyzer extracts the target age, characters, tone, theme, and safety constraints.  
The storyteller uses this plan to generate an age-appropriate bedtime story.  
The judge evaluates the story for age appropriateness, safety, bedtime tone, story arc, creativity, and alignment with the user request.  
If the judge score is below the threshold, the story is revised using the judge's feedback.