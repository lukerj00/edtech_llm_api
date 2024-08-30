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
            "correct_or_feedback": "discontent",
            "end": [
                993
            ],
            "incorrect_or_highlight": "disscontent",
            "start": [
                982
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
            "correct_or_feedback": "dissatisfaction",
            "end": [
                1199
            ],
            "incorrect_or_highlight": "disatisfaction",
            "start": [
                1185
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "This financial drain and public dissatisfaction significantly weakened",
            "end": [
                1226
            ],
            "incorrect_or_highlight": "This financial drain and public disatisfaction was significantly weakened",
            "start": [
                1153
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "The USA got involved, supporting the Afghan Mujahideen through Operation Cyclone, which included sending weapons and financial aid to fight the Soviets",
            "end": [
                280
            ],
            "incorrect_or_highlight": "The USA got involved, supporting the Afgan Mujahidene by sending them weapons and financial aid to fight the Soviets",
            "start": [
                164
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "This strategy by the USA, which intended to weaken Soviet influence, contributed to a prolonged war in Afghanistan, causing extensive suffering and chaos, and had long-term consequences for the region's stability",
            "end": [
                644
            ],
            "incorrect_or_highlight": "It's seen that this strategy by the USA, which intended to weaken Soviet influence, led to a prolonged war in Afganistan, causing extensive suffering and chaos",
            "start": [
                485
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "The Soviet Union spent an estimated 50 billion rubles (equivalent to $50 billion USD at the time) on the war, which severely strained their already struggling economy",
            "end": [
                890
            ],
            "incorrect_or_highlight": "Billions of dollars was poured into the military campaign, and the Soviet economy, which was not very strong to begin with, faced even more pressure",
            "start": [
                742
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "This financial drain and public dissatisfaction significantly weakened the Soviet Union's economic and political stability, contributing to its eventual decline and collapse in 1991",
            "end": [
                1329
            ],
            "incorrect_or_highlight": "This financial drain and public disatisfaction was significantly weakened the Soviet Union's economic and political stability, contributing to its eventual decline and collapse",
            "start": [
                1153
            ]
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "You've done a good job identifying two significant consequences of the Soviet invasion of Afghanistan. Your answer demonstrates a clear understanding of the impact on both international relations and the Soviet economy",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "To improve your answer, try to include more specific dates and figures where possible. For example, mentioning the exact year the Soviet Union collapsed (1991) would strengthen your argument",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "Consider expanding on the long-term consequences of the invasion, such as its impact on the balance of power in the region and its role in the end of the Cold War. This would demonstrate a deeper understanding of the historical significance of the event",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Your answer demonstrates features of the period and analyzes two consequences, showing good knowledge and understanding. This aligns with Level 2 (3-4 marks) in the mark scheme",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "You've provided specific information about the topic to support your explanation, such as the USA's support for the Mujahideen and the economic strain on the Soviet Union. This further supports a Level 2 assessment",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Based on the quality of your analysis and the specific information provided, I would award your answer 7 out of 8 marks (4 marks for each consequence). To achieve full marks, consider including more precise dates and figures, and explicitly linking your points to the end of the Cold War",
            "end": null,
            "incorrect_or_highlight": null,
            "start": null
        }
    ],
    "status": "completed",
    "submission": "Explain two consequences of the Soviet invasion of Afghanistan\n\nIn 1979, the Soviet Union's invasion of Afganistan seriously escalated\nCold War tensions even more. The USA got involved, supporting the\nAfgan Mujahidene by sending them weapons and financial aid to fight\nthe Soviets. This American support aimed to counter Soviet expansion,\nbut actually, it made the conflict in Afganistan much worse and more\ndrawn out, lasting until 1989 and creating a lot of instability in the area.\nIt's seen that this strategy by the USA, which intended to weaken\nSoviet influence, led to a prolonged war in Afganistan, causing\nextensive suffering and chaos.\n\nOn the economic side, the Soviet Union felt a massive strain because of\nthe war in Afganistan. Billions of dollars was poured into the military\ncampaign, and the Soviet economy, which was not very strong to begin\nwith, faced even more pressure. This was exacerbated by US economic\nsanctions. As war dragged on without a clear victory, disscontent grew\nwithin the Soviet Union. People began questioning the purpose and the\nhigh cost of continuing the war, leading to widespread critisicm of the\ngovernment. This financial drain and public disatisfaction was\nsignificantly weakened the Soviet Union's economic and political\nstability, contributing to its eventual decline and collapse."
}
'''
highlight_text(json_feedback)