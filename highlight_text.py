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
    "assistant_id": "asst_IVwvBg8sUi55Op1ZZvqGTTvf",
    "feedback": [
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "important",
            "end": [
                42
            ],
            "incorrect_or_highlight": "importent",
            "start": [
                33
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "were run",
            "end": [
                191
            ],
            "incorrect_or_highlight": "was run",
            "start": [
                184
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "policies",
            "end": [
                224
            ],
            "incorrect_or_highlight": "policys",
            "start": [
                217
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "free speech",
            "end": [
                295
            ],
            "incorrect_or_highlight": "free speach",
            "start": [
                284
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "reducing",
            "end": [
                309
            ],
            "incorrect_or_highlight": "reduceing",
            "start": [
                300
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "these changes",
            "end": [
                389
            ],
            "incorrect_or_highlight": "this changes",
            "start": [
                377
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "controlled",
            "end": [
                435
            ],
            "incorrect_or_highlight": "controled",
            "start": [
                426
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "going too far",
            "end": [
                527
            ],
            "incorrect_or_highlight": "going to far",
            "start": [
                515
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "countries",
            "end": [
                559,
                653
            ],
            "incorrect_or_highlight": "countrys",
            "start": [
                551,
                645
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "countries",
            "end": [
                559,
                653
            ],
            "incorrect_or_highlight": "countrys",
            "start": [
                551,
                645
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "keep control. This invasion",
            "end": [
                761
            ],
            "incorrect_or_highlight": "keep control This invasion",
            "start": [
                735
            ]
        },
        {
            "category": "SPaG",
            "citations": null,
            "colour": "orange",
            "correct_or_feedback": "its satellite states",
            "end": [
                986
            ],
            "incorrect_or_highlight": "it's satellite states",
            "start": [
                965
            ]
        }
    ],
    "status": "completed",
    "submission": "The Prague Spring of 1968 was an importent event in Czechoslovakia. It started when Alexander Dubček became the leader of the country. He wanted to make some changes to the way things was run. \\nDubček introduced new policys that gave people more freedom. This included allowing more free speach and reduceing government control. Many people in Czechoslovakia were happy about this changes. \\nHowever, the Soviet Union, which controled Czechoslovakia at the time, didn't like these reforms. They thought Dubček was going to far and worried that other countrys might want similar changes. \\nIn August 1968, the Soviet Union and other Warsaw Pact countrys sent tanks and soldiers into Czechoslovakia. They wanted to stop the reforms and keep control This invasion ended the Prague Spring. \\nAfter the invasion, Dubček was removed from power. The reforms were reversed, and Soviet control was tightend again. This event showed how much power the Soviet Union had over it's satellite states during the Cold War.",
    "thread_id": "thread_fjvTggvmyemdHWdCN8GXsAcH"
}
'''
highlight_text(json_feedback)