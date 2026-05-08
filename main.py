# import os
# import openai

# """
# Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

# """

# def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
#     openai.api_key = os.getenv("OPENAI_API_KEY") # please use your own openai api key here.
#     resp = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}],
#         stream=False,
#         max_tokens=max_tokens,
#         temperature=temperature,
#     )
#     return resp.choices[0].message["content"]  # type: ignore

# example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


# def main():
#     user_input = input("What kind of story do you want to hear? ")
#     response = call_model(user_input)
#     print(response)


# if __name__ == "__main__":
#     main()



import os
import json
from openai import OpenAI

MODEL = "gpt-3.5-turbo"
TTS_MODEL = "gpt-4o-mini-tts"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def call_model(prompt: str, max_tokens=1200, temperature=0.7) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY before running.")

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return resp.choices[0].message.content


def analyze_request(user_request: str) -> str:
    prompt = f"""
        You are a bedtime story analyzer.
        Analyze this request for a children's bedtime story:
        "{user_request}"
        Return a concise plan with:
        - likely target age between 5 and 10
        - main characters
        - story theme
        - emotional tone
        - safety constraints
        - suggested story arc
        """
    return call_model(prompt, temperature=0.2)


def generate_story(user_request: str, plan: str) -> str:
    prompt = f"""
        You are a warm, creative children's bedtime storyteller.
        Write a bedtime story for ages 5-10.
        User request:
        {user_request}
        Story plan:
        {plan}
        Requirements:
        - age appropriate for children 5-10
        - gentle bedtime tone
        - clear beginning, middle, and ending
        - include a small problem and a kind resolution
        - avoid scary, violent, or adult content
        - around 600-900 words
        - end with a calming final sentence
        """
    return call_model(prompt, temperature=0.8)


def judge_story(user_request: str, story: str) -> str:
    prompt = f"""
        You are an LLM judge evaluating a bedtime story for children ages 5-10.
        Original user request:
        {user_request}
        Story:
        {story}
        Evaluate the story using these criteria:
        1. Age appropriateness
        2. Bedtime tone
        3. Story arc
        4. Creativity
        5. Safety
        6. Whether it follows the user's request
        Return valid JSON only:
        {{
        "score": 1-10,
        "passes": true/false,
        "strengths": ["..."],
        "issues": ["..."],
        "revision_instructions": "..."
        }}
        """
    return call_model(prompt, temperature=0.1)

def revise_story_with_user_feedback(user_request: str, story: str, user_feedback: str) -> str:
    prompt = f"""
        You are collecting feedback from the user and revising a bedtime story for children ages 5-10.
        Original user request:
        {user_request}
        Current story:
        {story}
        User feedback:
        {user_feedback}
        Revise the story based on the user's feedback while keeping it:
        - age-appropriate for children 5-10
        - warm and gentle
        - suitable for bedtime
        - safe and non-scary
        - coherent with a clear beginning, middle, and ending
        Return only the revised final story.
        """
    return call_model(prompt, temperature=0.6)


def revise_story(user_request: str, story: str, judge_feedback: str) -> str:
    prompt = f"""
        Revise the bedtime story based on the judge feedback.
        Original user request:
        {user_request}
        Original story:
        {story}
        Judge feedback:
        {judge_feedback}
        Return only the improved final story.
        """
    return call_model(prompt, temperature=0.7)


def generate_voice(story: str, output_path: str = "bedtime_story.mp3") -> str:
    speech = client.audio.speech.create(
        model=TTS_MODEL,
        voice="marin",
        input=story,
        instructions=(
            "Read this as a warm, gentle bedtime storyteller. "
            "Use a calm pace, soft tone, and soothing emotional expression for children."
        ),
    )
    speech.write_to_file(output_path)
    return output_path


def main():
    user_request = input("What kind of bedtime story do you want to hear? ")

    plan = analyze_request(user_request)
    story = generate_story(user_request, plan)
    feedback = judge_story(user_request, story)

    try:
        feedback_json = json.loads(feedback)
        if not feedback_json.get("passes", False) or feedback_json.get("score", 0) < 8:
            story = revise_story(user_request, story, feedback)
    except json.JSONDecodeError:
        story = revise_story(user_request, story, feedback)

    print("\nFinal bedtime story:\n")
    print(story)

    user_feedback = input(
        "\nWould you like any changes? For example: make it shorter, gentler, funnier, "
        "add more animals, or characters, or type 'no' to keep it as is: "
    )

    if user_feedback.strip().lower() not in ["no", "n", "none", ""]:
        story = revise_story_with_user_feedback(user_request, story, user_feedback)
        print("\nRevised bedtime story:\n")
        print(story)

    audio_path = generate_voice(story)
    print(f"\nAudio story saved to: {audio_path}")

    print("\n---\nJudge feedback:\n")
    print(feedback)


if __name__ == "__main__":
    main()