from rich.text import Text
from rich.console import Console
import json
from collections import defaultdict

def blend_colors(colors):
    r = sum(int(c[1:3], 16) for c in colors) // len(colors)
    g = sum(int(c[3:5], 16) for c in colors) // len(colors)
    b = sum(int(c[5:7], 16) for c in colors) // len(colors)
    return f'#{r:02x}{g:02x}{b:02x}'

def highlight_text(json_feedback):
    data = json.loads(json_feedback)
    submission = data["submission"]
    feedback = data["feedback"]
    
    text = Text(submission)
    
    # Create a list to store all highlighting instructions
    highlights = []
    
    for correction in feedback:
        color = correction["colour"]
        if color.lower() == 'orange':
            color = '#FFA500'  # hex code for orange
        elif color.lower() == 'blue':
            color = '#89CFF0'
        
        start = correction.get("start")
        end = correction.get("end")
        
        if start is None or end is None:
            continue
        
        if isinstance(start, list) and isinstance(end, list):
            for s, e in zip(start, end):
                highlights.append((s, e, color))
        elif isinstance(start, int) and isinstance(end, int):
            highlights.append((start, end, color))
    
    # Sort highlights by start index
    highlights.sort(key=lambda x: x[0])
    
    # Merge overlapping highlights
    merged_highlights = defaultdict(list)
    for start, end, color in highlights:
        for i in range(start, end):
            merged_highlights[i].append(color)
    
    # Apply merged highlights
    current_color = None
    start = None
    
    for i in range(len(submission)):
        if i in merged_highlights:
            new_color = blend_colors(merged_highlights[i])
            if new_color != current_color:
                if start is not None:
                    text.stylize(f"on {current_color}", start, i)
                start = i
                current_color = new_color
        elif current_color is not None:
            text.stylize(f"on {current_color}", start, i)
            start = None
            current_color = None
    
    # Apply final highlight if it extends to the end
    if start is not None:
        text.stylize(f"on {current_color}", start, len(submission))
    
    Console().print(text)

# example usage
json_feedback = r'''
{
    "feedback": [
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "Afghanistan",
            "end": [
                114,
                387,
                605,
                740
            ],
            "incorrect_or_highlight": "Afganistan",
            "start": [
                104,
                377,
                595,
                730
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "Mujahideen",
            "end": [
                217
            ],
            "incorrect_or_highlight": "Mujahidene",
            "start": [
                207
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "Afghan",
            "end": [
                109,
                206,
                382,
                600,
                735
            ],
            "incorrect_or_highlight": "Afgan",
            "start": [
                104,
                201,
                377,
                595,
                730
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "criticism",
            "end": [
                1133
            ],
            "incorrect_or_highlight": "critisicm",
            "start": [
                1124
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "discontent",
            "end": [],
            "incorrect_or_highlight": "discontent",
            "start": []
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "significantly weakened",
            "end": [
                1226
            ],
            "incorrect_or_highlight": "was significantly weakened",
            "start": [
                1200
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "billions of dollars were",
            "end": [
                765
            ],
            "incorrect_or_highlight": "billions of dollars was",
            "start": [
                742
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "the conflict in Afghanistan much worse and more drawn out, lasting until the Soviet withdrawal in 1989",
            "end": [
                437
            ],
            "incorrect_or_highlight": "the conflict in Afganistan much worse and more drawn out, lasting until 1989",
            "start": [
                361
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "creating significant instability in the region",
            "end": [
                483
            ],
            "incorrect_or_highlight": "creating a lot of instability in the area",
            "start": [
                442
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "the Soviet economy, which was already under strain",
            "end": [
                864
            ],
            "incorrect_or_highlight": "the Soviet economy, which was not very strong to begin with",
            "start": [
                805
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "US-led economic sanctions",
            "end": [
                937
            ],
            "incorrect_or_highlight": "US economic sanctions",
            "start": [
                916
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "leading to widespread criticism of the Soviet government",
            "end": [
                1151
            ],
            "incorrect_or_highlight": "leading to widespread critisicm of the government",
            "start": [
                1102
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "contributing to the eventual dissolution of the Soviet Union in 1991",
            "end": [
                1329
            ],
            "incorrect_or_highlight": "contributing to its eventual decline and collapse",
            "start": [
                1280
            ]
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "I suggest providing more specific examples of how the US support for the Mujahideen impacted the conflict, such as mentioning the types of weapons supplied or key battles influenced by this support",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "It would be beneficial to include some statistics or quotes from historical figures to strengthen your points about the economic strain on the Soviet Union",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "To improve your analysis, try to explain the broader geopolitical consequences of the Soviet invasion, such as its impact on US-Soviet relations and the Cold War dynamics",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "You have demonstrated a good understanding of the period and provided specific information about the consequences of the Soviet invasion of Afghanistan, which aligns with Level 2 of the mark scheme",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Your analysis of the economic strain on the Soviet Union and the prolonged conflict in Afghanistan shows a clear grasp of the cause and effect, which is essential for achieving higher marks",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Based on the mark scheme, I would estimate your response to be in the 3-4 mark range for each consequence, giving a total of 6-8 marks out of 8",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        }
    ],
    "status": "completed",
    "submission": "Explain two consequences of the Soviet invasion of Afghanistan\n\nIn 1979, the Soviet Union's invasion of Afganistan seriously escalated Cold War tensions even more. The USA got involved, supporting the Afgan Mujahidene by sending them weapons and financial aid to fight the Soviets. This American support aimed to counter Soviet expansion, but actually, it made the conflict in Afganistan much worse and more drawn out, lasting until 1989 and creating a lot of instability in the area. It's seen that this strategy by the USA, which intended to weaken Soviet influence, led to a prolonged war in Afganistan, causing extensive suffering and chaos.\n\nOn the economic side, the Soviet Union felt a massive strain because of the war in Afganistan. Billions of dollars was poured into the military campaign, and the Soviet economy, which was not very strong to begin with, faced even more pressure. This was exacerbated by US economic sanctions. As war dragged on without a clear victory, disscontent grew within the Soviet Union. People began questioning the purpose and the high cost of continuing the war, leading to widespread critisicm of the government. This financial drain and public disatisfaction was significantly weakened the Soviet Union's economic and political stability, contributing to its eventual decline and collapse."
}
'''
highlight_text(json_feedback)