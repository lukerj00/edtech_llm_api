from rich.text import Text
from rich.console import Console
import json
from collections import defaultdict
import traceback

def blend_colors(colors):
    r = sum(int(c[1:3], 16) for c in colors) // len(colors)
    g = sum(int(c[3:5], 16) for c in colors) // len(colors)
    b = sum(int(c[5:7], 16) for c in colors) // len(colors)
    return f'#{r:02x}{g:02x}{b:02x}'

def highlight_text(json_feedback, submission):
    try:
        feedback = json.loads(json_feedback)
        # use repr() to get string representation
        submission_repr = repr(submission)[1:-1]  # remove outer quotes
        text_repr = Text(submission_repr)
        
        # create a list to store all highlighting instructions
        highlights = []
        
        for correction in feedback["corrections"]:
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
            else:
                print(f"Warning: Unexpected type for start or end in correction: {correction}")
        
        # sort highlights by start index
        highlights.sort(key=lambda x: x[0])
        
        # merge overlapping highlights
        merged_highlights = defaultdict(list)
        for start, end, color in highlights:
            for i in range(start, end):
                merged_highlights[i].append(color)
        
        # apply merged highlights
        current_color = None
        start_repr = None
        
        for i in range(len(submission_repr)):
            if i in merged_highlights:
                new_color = blend_colors(merged_highlights[i])
                if new_color != current_color:
                    if start_repr is not None:
                        text_repr.stylize(f"on {current_color}", start_repr, i)
                    start_repr = i
                    current_color = new_color
            elif current_color is not None:
                text_repr.stylize(f"on {current_color}", start_repr, i)
                start_repr = None
                current_color = None
        
        # apply final highlight if it extends to the end
        if start_repr is not None:
            text_repr.stylize(f"on {current_color}", start_repr, len(submission_repr))
        
        Console().print(text_repr)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()

# example usage
json_feedback = '''
{
    "corrections": [
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "Afghanistan",
            "end": [
                50,
                323,
                541,
                677
            ],
            "incorrect": "Afganistan",
            "start": [
                40,
                313,
                531,
                667
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "further escalated Cold War tensions",
            "end": [
                98
            ],
            "incorrect": "escalated Cold War tensions even more",
            "start": [
                61
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "Mujahideen",
            "end": [
                153
            ],
            "incorrect": "Mujahidene",
            "start": [
                143
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "criticism",
            "end": [
                1070
            ],
            "incorrect": "critisicm",
            "start": [
                1061
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "discontent",
            "end": [
                930
            ],
            "incorrect": "disscontent",
            "start": [
                919
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "significantly weakened",
            "end": [
                1163
            ],
            "incorrect": "was significantly weakened",
            "start": [
                1137
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "creating significant instability in the region",
            "end": [
                419
            ],
            "incorrect": "creating a lot of instability in the area",
            "start": [
                378
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "eventual collapse",
            "end": [
                1266
            ],
            "incorrect": "collapse",
            "start": [
                1258
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "billions of dollars were poured",
            "end": [
                709
            ],
            "incorrect": "billions of dollars was poured",
            "start": [
                679
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "financial aid, to fight the Soviets",
            "end": [
                216
            ],
            "incorrect": "financial aid to fight the Soviets",
            "start": [
                182
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "U.S. economic sanctions",
            "end": [
                874
            ],
            "incorrect": "US economic sanctions",
            "start": [
                853
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "In 1979, the Soviet Union's invasion of Afghanistan marked the end of détente and seriously escalated Cold War tensions",
            "end": [
                98
            ],
            "incorrect": "In 1979, the Soviet Union's invasion of Afganistan seriously escalated Cold War tensions even more",
            "start": [
                0
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "The USA became involved",
            "end": [
                120
            ],
            "incorrect": "The USA got involved",
            "start": [
                100
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "supporting the Afghan Mujahideen by sending them weapons and financial aid through Operation Cyclone to fight the Soviets",
            "end": [
                216
            ],
            "incorrect": "supporting the Afgan Mujahidene by sending them weapons and financial aid to fight the Soviets",
            "start": [
                122
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "This American support aimed to counter Soviet expansion and contributed to a prolonged conflict in Afghanistan",
            "end": [
                353
            ],
            "incorrect": "This American support aimed to counter Soviet expansion, but actually, it made the conflict in Afganistan much worse and more drawn out",
            "start": [
                218
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "contributing significantly to instability in the region",
            "end": [
                419
            ],
            "incorrect": "creating a lot of instability in the area",
            "start": [
                378
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "U.S. economic sanctions and a boycott of the 1980 Moscow Olympics",
            "end": [
                874
            ],
            "incorrect": "US economic sanctions",
            "start": [
                853
            ]
        },
        {
            "category": "historical_accuracy",
            "citations": null,
            "colour": "blue",
            "correct_or_feedback": "As the war dragged on without a clear victory, discontent grew within the Soviet Union as citizens began questioning the purpose and high costs of the war",
            "end": [
                1037
            ],
            "incorrect": "As war dragged on without a clear victory, disscontent grew within the Soviet Union. People began questioning the purpose and the high cost of continuing the war",
            "start": [
                876
            ]
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "I suggest further elaborating on the specific ways the Soviet invasion of Afghanistan impacted global politics, such as detailing the shift in U.S. foreign policy",
            "end": null,
            "incorrect": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "It would be beneficial to include more precise dates and events to strengthen your points, like the timeline of U.S. involvement or specific battles in the Afghan war",
            "end": null,
            "incorrect": null,
            "start": null
        },
        {
            "category": "overall_comments",
            "citations": null,
            "colour": "green",
            "correct_or_feedback": "To improve your analysis, consider discussing the long-term effects of the invasion on Afghanistan itself, including the social and political aftermath",
            "end": null,
            "incorrect": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Your answer demonstrates good knowledge of the topic and includes specific information about the Soviet invasion and its consequences. This aligns with Level 2 criteria",
            "end": null,
            "incorrect": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Both consequences are correctly identified and analyzed, showing features of the period and how they connect to the outcome, which satisfies AO2 requirements",
            "end": null,
            "incorrect": null,
            "start": null
        },
        {
            "category": "marking",
            "citations": null,
            "colour": "purple",
            "correct_or_feedback": "Given the depth of analysis and accurate historical context, I would estimate your answer would achieve around 6-7 marks out of 8, as there is room to develop some points further and clarify the impact of U.S. actions more precisely",
            "end": null,
            "incorrect": null,
            "start": null
        }
    ],
    "status": "completed"
}
'''

submission = "In 1979, the Soviet Union's invasion of Afganistan seriously escalated Cold War tensions even more. The USA got involved, supporting the Afgan Mujahidene by sending them weapons and financial aid to fight the Soviets. This American support aimed to counter Soviet expansion, but actually, it made the conflict in Afganistan much worse and more drawn out, lasting until 1989 and creating a lot of instability in the area. It's seen that this strategy by the USA, which intended to weaken Soviet influence, led to a prolonged war in Afganistan, causing extensive suffering and chaos. \nOn the economic side, the Soviet Union felt a massive strain because of the war in Afganistan. Billions of dollars was poured into the military campaign, and the Soviet economy, which was not very strong to begin with, faced even more pressure. This was exacerbated by US economic sanctions. As war dragged on without a clear victory, disscontent grew within the Soviet Union. People began questioning the purpose and the high cost of continuing the war, leading to widespread critisicm of the government. This financial drain and public disatisfaction was significantly weakened the Soviet Union's economic and political stability, contributing to its eventual decline and collapse."
highlight_text(json_feedback, submission)
