import json, random, copy

def shuffle_choices(quiz_dict, seed=None):
    """
    Return a deep-copied quiz dict whose per-question `choices` lists
    are shuffled. All text content (including targets) is preserved.
    """
    q2 = copy.deepcopy(quiz_dict)
    rng = random.Random(seed)
    for q in q2["questions"]:
        rng.shuffle(q["choices"])
        # sanity check: ensure all targets still present after shuffle
        for t in q["target"]:
            if t not in q["choices"]:
                raise ValueError(f"Target missing after shuffle in question {q['id']}")
    return q2

# --- your original quiz JSON pasted here ---
quiz = """{
  "instructions": "In this test, you will be presented with a series of definitions. For each definition, your task is to select the English word that best matches it from the list of options provided. Read each definition carefully and choose the word that fits best. Take your time and do your best. If everything is clear, you can now start the experiment.",
  "question_display": "word_only",
  "questions": [
    {
      "id": "To separate into parts",
      "type": "choice",
      "feedback": true,
      "choices": ["divide", "stack", "sausage", "retire"],
      "target": ["divide"]
    },
    {
      "id": "A retail establishment that sells medicines toiletries and other household goods",
      "type": "choice",
      "feedback": true,
      "choices": ["drugstore", "toothbrush", "childhood", "roughly"],
      "target": ["drugstore"]
    },
    {
      "id": "A representation of something often on a smaller scale",
      "type": "choice",
      "feedback": true,
      "choices": ["model", "task", "unless", "sports"],
      "target": ["model"]
    },
    {
      "id": "The art or practice of designing and constructing buildings",
      "type": "choice",
      "feedback": true,
      "choices": ["architecture", "market", "audience", "reply"],
      "target": ["architecture"]
    },
    {
      "id": "Given",
      "type": "choice",
      "feedback": true,
      "choices": ["provided", "sign", "helpful", "retail"],
      "target": ["provided"]
    },
    {
      "id": "A three-dimensional work of art typically representing a person or animal",
      "type": "choice",
      "feedback": true,
      "choices": ["statue", "hardly", "quiz", "accept"],
      "target": ["statue"]
    },
    {
      "id": "The difference between two things",
      "type": "choice",
      "feedback": true,
      "choices": ["contrast", "predict", "release", "anywhere"],
      "target": ["contrast"]
    },
    {
      "id": "A celestial body that orbits a star is massive enough to be rounded by its own gravity and has cleared the neighborhood around its orbit",
      "type": "choice",
      "feedback": true,
      "choices": ["planet", "appear", "pilot", "ahead"],
      "target": ["planet"]
    },
    {
      "id": "Be deprived of or cease to have",
      "type": "choice",
      "feedback": true,
      "choices": ["lose", "crown", "place", "crime"],
      "target": ["lose"]
    },
    {
      "id": "To stop doing something",
      "type": "choice",
      "feedback": true,
      "choices": ["quit", "mushroom", "honey", "length"],
      "target": ["quit"]
    },
    {
      "id": "A polite word used to make a request more courteous",
      "type": "choice",
      "feedback": true,
      "choices": ["please", "softly", "stomachache", "homework"],
      "target": ["please"]
    },
    {
      "id": "Taking part in or connected with something",
      "type": "choice",
      "feedback": true,
      "choices": ["involved", "income", "release", "customer"],
      "target": ["involved"]
    },
    {
      "id": "A finely ground powder made from grains",
      "type": "choice",
      "feedback": true,
      "choices": ["flour", "badly", "feelings", "cheek"],
      "target": ["flour"]
    },
    {
      "id": "At an unspecified time in the future",
      "type": "choice",
      "feedback": true,
      "choices": ["someday", "painter", "speak", "slender"],
      "target": ["someday"]
    }
  ]
}
"""


# shuffle deterministically
shuffled_quiz = shuffle_choices(json.loads(quiz), seed=42)

# print as JSON
print(json.dumps(shuffled_quiz, indent=2, ensure_ascii=False))
