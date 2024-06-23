import re
import json

qualification = "GCSE"
subject = "history"

messages = {
        "SPaG": {
            'role': 'user',
            'content': f"""
            1. Spelling, Punctuation and Grammar: give corrections for poor spelling, punctuation and grammar, bullet pointed in the exact following format: `- incorrect word\phrase -> correct word/phrase`. 
            Give feedback only for the category stated above, and only in the bullet-point format requested (do NOT include any other feedback in addition to the bullet points of form described above).
            Give as many corrections as necessary (but only one point per correction even if the error occurs multiple times), appropriate for a student of {qualification}-level {subject}.
            """,
        },
        "historical_accuracy": {
            'role': 'user',
            'content': f"""
            2. Historical Accuracy and Analysis of Cause and Effect: give corrections for any errors in historical accuracy, time period awareness or logical analysis of cause and effect, bullet pointed in the exact following format: `- incorrect fact/logic -> correct fact/logic`.
            Give feedback only for the category stated above, and only in the bullet-point format requested (do NOT include any other feedback in addition to the bullet points of form described above).
            Give as many corrections as necessary, appropriate for a student of {qualification}-level {subject}.
            """,
        },
        "overall_comments": {
            'role': 'user',
            'content': f"""
            3. Overall Comments and Areas for Improvement: give overall comments and suggestions for how the student could improve their work, bullet pointed in the exact following format: `- suggestion`.
            Give feedback only for the category stated above, and only in the bullet-point format requested (do NOT include any other feedback in addition to the bullet points of form described above).
            Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
            """,
        },
        "marking": {
            'role': 'user',
            'content': f"""
            4. Marking: give estimated marks carefully taking into account the mark scheme attached, bullet pointed in the exact following format: `- marking feedback comment`.
            Give feedback only for the category stated above, and only in the bullet-point format requested (do NOT include any other feedback in addition to the bullet points of form described above).
            Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
            """,
        },
    }

output = {
    "SPaG": "1. Spelling, Punctuation and Grammar:\n\n- `Afganistan` -> `Afghanistan`\n- `Afgan` -> `Afghan`\n- `Afgan Mujahidene` -> `Afghan Mujahideen`\n- `was poured` -> `were poured`\n- `critisicm` -> `criticism`\n- `disatisfaction` -> `dissatisfaction`\n- `was significantly weakened` -> `significantly weakened`\n- `USA got` -> `USA became`\n- `On the economic side,` -> `On the economic front,`\n- `It's seen that` -> `It is evident that`\n- `lasted until 1989 and creating` -> `lasted until 1989, creating`\n- `As war dragged on` -> `As the war dragged on`\n\nThis enhances the clarity and accuracy of your assignment, making it more suitable for GCSE-level history.",
    "historical_accuracy": "2. Historical Accuracy and Analysis of Cause and Effect:\n\n- `supporting the Afgan Mujahidene by sending them weapons and financial aid` -> `supporting the Afghan Mujahideen by sending them weapons and financial aid through Operation Cyclone`\n- `the Soviet economy, which was not very strong to begin with` -> `the Soviet economy, which was already under strain due to existing economic issues`\n- `People began questioning the purpose and the high cost of continuing the war, leading to widespread critisicm of the government` -> `People began questioning the purpose and the high cost of continuing the war, leading to widespread criticism and protests within the Soviet Union`\n\nYour analysis should also consider the broader geopolitical impact of the invasion, such as the ending of détente and the issuance of the Carter Doctrine by the USA【9:0†source】【9:1†source】.",
    "marking": "3. Marking feedback comment: The submission shows good knowledge of the period and explains consequences of the Soviet invasion of Afghanistan effectively. However, it lacks some specific details, such as the Carter Doctrine and the US boycott of the 1980 Moscow Olympic Games, which would have strengthened the explanation.\n- Marking feedback comment: The analysis is clear, but the logical connections between the facts can be improved to better demonstrate the cause-and-effect relationships, particularly concerning the broader geopolitical impact.\n- Marking feedback comment: The answer falls within Level 2 of the mark scheme, with specific features analyzed and good knowledge demonstrated. However, more specific supporting details and a clearer articulation of the broader consequences are needed to achieve the highest marks in this level【15:0†example-ms.pdf】.",
    "overall_comments": "4. Overall Comments and Areas for Improvement:\n\n- Suggestion: Ensure that all historical names and terms, such as \"Afghanistan\" and \"Mujahideen,\" are spelled correctly throughout your work to maintain accuracy and clarity.\n- Suggestion: Provide more detailed analysis of the geopolitical consequences of the invasion, such as the impact on US-Soviet relations and the end of détente, to enhance the depth of your response.\n- Suggestion: Use more varied vocabulary and more complex sentence structures to demonstrate higher-level writing skills and to better articulate the cause-and-effect relationships in your analysis."
}

output2 =  {
    "SPaG": '```json\n{\n    "Spelling, Punctuation and Grammar": [\n        "- Afganistan -> Afghanistan",\n        "- Mujahidene -> Mujahideen",\n        "- Afgan -> Afghan",\n        "- its seen -> It\'s seen",\n        "- Afganistan -> Afghanistan",\n        "- economic side -> economic aspect",\n        "- Afganistan -> Afghanistan",\n        "- this was -> this\',\n        "- critisicm -> criticism",\n        "- disatisfaction -> dissatisfaction"\n    ]\n}\n```',
    "historical_accuracy": '```json\n{\n    "Historical Accuracy and Analysis of Cause and Effect": [\n        "- The USA got involved, supporting the Afghan Mujahideen by sending them weapons and financial aid to fight the Soviets -> The USA became involved by supporting the Mujahideen through Operation Cyclone, which included sending weapons and financial aid to combat Soviet forces.",\n        "- lasting until 1989 and creating a lot of instability in the area -> lasting until 1989, contributing significantly to regional instability and the eventual emergence of extremist groups like the Taliban.",\n        "- It\'s seen that this strategy by the USA, which intended to weaken Soviet influence, led to a prolonged war in Afghanistan -> This US strategy, aimed at curbing Soviet influence, indeed contributed to a prolonged conflict, complicating withdraw and post-war stability efforts.",\n        "- Billions of dollars was poured into the military campaign -> The Soviet Union invested billions of rubles into the Afghan conflict.",\n        "- the Soviet economy, which was not very strong to begin with, faced even more pressure -> the already struggling Soviet economy faced even greater strain due to the costs associated with the prolonged war.",\n        "- As war dragged on without a clear victory, discontent grew within the Soviet Union -> As the war continued without a decisive victory, public discontent within the Soviet Union grew.",\n        "- This financial drain and public dissatisfaction was significantly weakened the Soviet Union\'s economic and political stability, contributing to its eventual decline and collapse -> This financial drain and escalating public dissatisfaction significantly weakened the Soviet Union\'s economic and political stability, accelerating its eventual decline and contributing to the dissolution in 1991."\n    ]\n}\n```',
    "marking": '```json\n{\n    "Overall Comments and Areas for Improvement": [\n        "- Be precise with historical details, such as the names of operations and exact economic impacts; it shows a deeper understanding of the subject.",\n        "- Try to structure your paragraphs more clearly, starting with a topic sentence that outlines the consequence you are discussing; this will make your argument clearer and more persuasive.",\n        "- Consider providing more evidence and examples to support your points, such as statistics or quotes from historians, to strengthen your analysis and make your essay more compelling."\n    ]\n}\n```',
    "overall_comments": '```json\n{\n    "Marking": [\n        "- Good explanation of the consequences, showing clear understanding and analysis, which places your answer in Level 2 (3-4 marks per consequence).",\n        "- While the explanations are relevant, including specific details such as the Carter Doctrine and the US boycott of the 1980 Moscow Olympics could elevate your answer to the higher end of the mark range.",\n        "- Overall, I would estimate a mark of 6 out of 8, since the explanations are well-developed but could benefit from some additional precise details to reach the highest level."\n    ]\n}\n```'
    }

output3 = {
    '{\n    "Spelling, Punctuation and Grammar": [\n        "- Afganistan -> Afghanistan",\n        "- Mujahidene -> Mujahideen",\n        "- Soviet Union\'s -> Soviet Union’s",\n        "- but actually, -> but, actually,",\n        "- Afganistan much -> Afghanistan much",\n        "- campaign, and -> campaign; and",\n        "- critisicm -> criticism",\n        "- disatisfaction -> dissatisfaction",\n        "- It\'s seen that -> It’s seen that"\n    ]\n}', '{\n    "Historical Accuracy and Analysis of Cause and Effect": [\n        "- Soviet invasion of Afghanistan in 1979 escalated Cold War tensions -> The Soviet invasion of Afghanistan in 1979 intensified the Cold War tensions",\n        "- American support aimed to counter Soviet expansion, but actually, it made the conflict much worse -> American support aimed to counter Soviet expansion, prolonging the conflict until 1989",\n        "- instability in the area. -> instability in the region",\n        "- This strategy by the USA intended to weaken Soviet influence -> This strategy intended by the USA to weaken Soviet influence led to a prolonged conflict",\n        "- creating a lot of instability in the area -> creating widespread instability",\n        "- Soviet Union felt massive strain because of the war -> Soviet Union experienced significant strain due to the war in Afghanistan",\n        "- Billions of dollars was poured into the military campaign -> Billions of dollars were poured into the military campaign",\n        "- US economic sanctions -> economic sanctions imposed by the US",\n        "- high cost of continuing the war, leading to widespread criticism of the government -> high cost of continuing the war, which led to widespread criticism of the government",\n        "- disatisfaction led to a significant weakening of the Soviet Union\'s economic and political stability, contributing to its decline -> dissatisfaction significantly weakened the Soviet Union’s economic and political stability, contributing to its eventual collapse"\n    ]\n}', '{\n    "Overall Comments and Areas for Improvement": [\n        "- Strengthen your arguments by adding more specific historical details and evidence. This will enhance the depth of your explanation.",\n        "- Improve the clarity of your sentences by avoiding overly complex structures and ensuring each sentence clearly follows from the previous one.",\n        "- Make sure to thoroughly proofread your work to catch any spelling and grammatical errors that may distract from your historical analysis."\n    ]\n}', '{\n    "Marking": [\n        "- Your explanation includes several simple or generalised comments about the consequences of the Soviet invasion of Afghanistan, corresponding to Level 1 (1-2 marks) based on the mark scheme."\n    ]\n}'
    }

def format_output_OLD(output, key, message):
    colour_dict = {
        "SPaG": "orange",
        "historical_accuracy": "blue",
        "overall_comments": "green",
        "marking": "purple",
    }
    response_data = []
    content = re.sub(r'^[^:]*:\n\n', '', output, count=1)
    bullets = re.findall(r'- (.+?)(?=\n- |\n\n|$)', content, re.DOTALL)

    bullets_list = []
    for bullet in bullets:
        pattern = r'【([^】]+)】'
        match = re.search(pattern, bullet)
        if match:
            citations = match.group(1)
            bullet = re.sub(pattern, '', bullet).strip()
        else:
            citations = None
        
        if key in ['SPaG','historical_accuracy']:
            parts = re.split(r' -> ', bullet, maxsplit=1)
            if len(parts) == 2:
                incorrect_response, correct_response = parts
                incorrect_response, correct_response = incorrect_response.strip().strip('`'), correct_response.strip().strip('`')
                incorrect_response, correct_response = re.sub(r'^\s*\*+\s*', '', incorrect_response), re.sub(r'^\s*\*+\s*', '', correct_response)
                incorrect_response, correct_response = incorrect_response.strip(r'/.*\"'), correct_response.strip(r'/.*\"')
                bullets_list.append((incorrect_response, correct_response))
                start_indices = [match.start() for match in re.finditer(re.escape(incorrect_response), output)]
                response_data.append(
                    {
                        'category': key,
                        'incorrect': incorrect_response,
                        'correct_or_feedback': correct_response,
                        'citations': citations,
                        'start': start_indices,
                        'end': [ind + len(bullet) for ind in start_indices],
                        'colour': colour_dict.get(key),
                    }
                )
            else:
                raise ValueError(f"LLM output correction '{bullet}' does not contain ' -> ' character")
            
        elif key in ['marking', 'overall_comments']:
            bullet = bullet.strip().strip('`')
            colon_index = bullet.find(':')
            if colon_index != -1:
                bullet = bullet[colon_index+1:].strip()
            else:
                bullet = bullet.strip()
            bullet = re.sub(r'^\s*\*+\s*', '', bullet)
            bullet = bullet.strip(r'/.*\"')
            bullet = re.sub(r'(?<!^)\"(?!$)', "'", bullet)
            bullets_list.append(bullet)
            start_indices = [match.start() for match in re.finditer(re.escape(bullet), output)]
            response_data.append(
                {
                    'category': key,
                    'incorrect': None,
                    'correct_or_feedback': bullet,
                    'citations': citations,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(key),
                }
            )
        else:
            raise ValueError(f"Invalid key '{key}'")
    
    return response_data

def format_output_old(output, key):
    colour_dict = {
        "SPaG": "orange",
        "historical_accuracy": "blue",
        "overall_comments": "green",
        "marking": "purple",
    }
    response_data = []
    content = re.sub(r'^[^:]*:\n\n', '', output, count=1)
    bullets = re.findall(r'- (.+?)(?=\n- |\n\n|$)', content, re.DOTALL)

    bullets_list = []
    for bullet in bullets:
        pattern = r'【([^】]+)】'
        match = re.search(pattern, bullet)
        if match:
            citations = match.group(1)
            bullet = re.sub(pattern, '', bullet).strip()
        else:
            citations = None
        
        if key in ['SPaG','historical_accuracy']:
            parts = re.split(r' -> ', bullet, maxsplit=1)
            if len(parts) == 2:
                incorrect_response, correct_response = parts
                incorrect_response, correct_response = incorrect_response.strip().strip('`'), correct_response.strip().strip('`')
                incorrect_response, correct_response = re.sub(r'^\s*\*+\s*', '', incorrect_response), re.sub(r'^\s*\*+\s*', '', correct_response)
                incorrect_response, correct_response = incorrect_response.strip(r'/.*\"'), correct_response.strip(r'/.*\"')
                bullets_list.append((incorrect_response, correct_response))
                start_indices = [match.start() for match in re.finditer(re.escape(incorrect_response), output)]
                response_data.append(
                    {
                        'category': key,
                        'incorrect': incorrect_response,
                        'correct_or_feedback': correct_response,
                        'citations': citations,
                        'start': start_indices,
                        'end': [ind + len(bullet) for ind in start_indices],
                        'colour': colour_dict.get(key),
                    }
                )
            else:
                raise ValueError(f"LLM output correction '{bullet}' does not contain ' -> ' character")
            
        elif key in ['marking', 'overall_comments']:
            bullet = bullet.strip().strip('`')
            colon_index = bullet.find(':')
            if colon_index != -1:
                bullet = bullet[colon_index+1:].strip()
            else:
                bullet = bullet.strip()
            bullet = re.sub(r'^\s*\*+\s*', '', bullet)
            bullet = bullet.strip(r'/.*\"')
            bullet = re.sub(r'(?<!^)\"(?!$)', "'", bullet)
            bullets_list.append(bullet)
            start_indices = [match.start() for match in re.finditer(re.escape(bullet), output)]
            response_data.append(
                {
                    'category': key,
                    'incorrect': None,
                    'correct_or_feedback': bullet,
                    'citations': citations,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(key),
                }
            )
        else:
            raise ValueError(f"Invalid key '{key}'")
    
    return response_data

def format_outputa(output, key):
    colour_dict = {
        "SPaG": "orange",
        "historical_accuracy": "blue",
        "overall_comments": "green",
        "marking": "purple",
    }
    response_data = []

    # Strip the markdown code block formatting and clean the JSON string
    json_str = re.sub(r'^```json\n|\n```$', '', output)
    
    # Replace problematic characters and ensure proper escaping
    json_str = json_str.replace('\n', '').replace('\t', '').replace('\'', '"')

    # Parse JSON
    try:
        content_dict = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")

    # Extract category-specific data
    category_key_map = {
        "SPaG": "Spelling, Punctuation and Grammar",
        "historical_accuracy": "Historical Accuracy and Analysis of Cause and Effect",
        "overall_comments": "Overall Comments and Areas for Improvement",
        "marking": "Marking"
    }

    category_key = category_key_map.get(key)
    if not category_key:
        raise ValueError(f"Invalid key '{key}'")

    category_data = content_dict.get(category_key, [])

    for bullet in category_data:
        pattern = r'【([^】]+)】'
        match = re.search(pattern, bullet)
        if match:
            citations = match.group(1)
            bullet = re.sub(pattern, '', bullet).strip()
        else:
            citations = None

        if key in ['SPaG', 'historical_accuracy']:
            parts = re.split(r' -> ', bullet, maxsplit=1)
            if len(parts) == 2:
                incorrect_response, correct_response = parts
                print('inc=', incorrect_response, 'c=', correct_response)
                incorrect_response = incorrect_response.strip().strip('`').strip(r'/.*\"').lstrip('*').strip()
                print('inc=', incorrect_response, 'c=', correct_response)
                correct_response = correct_response.strip().strip('`').strip(r'/.*\"').lstrip('*').strip()
                print('inc=', incorrect_response, 'c=', correct_response)
                response_data.append(
                    {
                        'category': key,
                        'incorrect': incorrect_response,
                        'correct_or_feedback': correct_response,
                        'citations': citations,
                        'start': None,
                        'end': None,
                        'colour': colour_dict.get(key),
                    }
                )
            else:
                raise ValueError(f"LLM output correction '{bullet}' does not contain ' -> ' character")

        elif key in ['overall_comments', 'marking']:
            bullet = bullet.strip().strip('`').lstrip('*').strip()
            if key == 'overall_comments':
                colon_index = bullet.find(':')
                if colon_index != -1:
                    bullet = bullet[colon_index+1:].strip()
            bullet = re.sub(r'(?<!^)\"(?!$)', "'", bullet)
            response_data.append(
                {
                    'category': key,
                    'incorrect': None,
                    'correct_or_feedback': bullet,
                    'citations': citations,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(key),
                }
            )
        else:
            raise ValueError(f"Invalid key '{key}'")

    return response_data

def format_output(output, key):
    colour_dict = {
        "SPaG": "orange",
        "historical_accuracy": "blue",
        "overall_comments": "green",
        "marking": "purple",
    }
    response_data = []

    # Clean up the JSON content
    json_content = output.strip('```json\n').strip()
    
    # Replace single quotes with double quotes, but not within words
    json_content = re.sub(r"(?<!\w)'(?![\w\s])|(?<=\s)'|'(?=\s|$)", '"', json_content)
    
    # Handle the case where a single quote is used within a word (e.g., "It's")
    json_content = re.sub(r"(\w)'(\w)", r"\1'\2", json_content)

    try:
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error for key {key}: {e}")
        print(f"Problematic JSON content: {json_content}")
        return []

    json_key = list(data.keys())[0]
    bullets = data[json_key]

    for bullet in bullets:
        bullet = bullet.strip('- ').strip()
        
        if key in ['SPaG', 'historical_accuracy']:
            parts = re.split(r' -> ', bullet, maxsplit=1)
            if len(parts) == 2:
                incorrect_response, correct_response = parts
                incorrect_response = incorrect_response.strip().strip('`')
                correct_response = correct_response.strip().strip('`')
                
                response_data.append({
                    'category': key,
                    'incorrect': incorrect_response,
                    'correct_or_feedback': correct_response,
                    'citations': None,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(key),
                })
            else:
                print(f"Warning: LLM output correction '{bullet}' does not contain ' -> ' character")
        
        elif key in ['marking', 'overall_comments']:
            response_data.append({
                'category': key,
                'incorrect': None,
                'correct_or_feedback': bullet,
                'citations': None,
                'start': None,
                'end': None,
                'colour': colour_dict.get(key),
            })
        
        else:
            print(f"Warning: Invalid key '{key}'")

    return response_data

import json
import re

def format_output_new(output, key):
    colour_dict = {
        "SPaG": "orange",
        "historical_accuracy": "blue",
        "overall_comments": "green",
        "marking": "purple",
    }
    response_data = []

    # # Clean up the JSON content
    # json_content = output.strip('```json\n').strip()
    
    # # Replace single quotes with double quotes for the entire JSON structure
    # json_content = re.sub(r"(?<!\\)'", '"', json_content)
    
    # # Handle escaped single quotes within words
    # json_content = json_content.replace("\\'", "'")

    # Clean up the JSON content
    json_content = output.strip('```json\n').strip()
    
    # Replace single quotes with double quotes for the entire JSON structure
    json_content = re.sub(r"(?<!\\)'", '"', json_content)
    
    # Handle escaped single quotes within words
    json_content = json_content.replace("\\'", "'")
    
    # Escape any unescaped double quotes within string content
    json_content = re.sub(r'(?<!\\)(")((?:.(?!(?<!\\)"))*.)(")', lambda m: m.group(1) + m.group(2).replace('"', '\\"') + m.group(3), json_content)

    try:
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error for key {key}: {e}")
        print(f"Problematic JSON content: {json_content}")
        return []

    json_key = list(data.keys())[0]
    bullets = data[json_key]

    for bullet in bullets:
        bullet = bullet.strip('- ').strip()
        
        if key in ['SPaG', 'historical_accuracy']:
            parts = re.split(r' -> ', bullet, maxsplit=1)
            if len(parts) == 2:
                incorrect_response, correct_response = parts
                incorrect_response = incorrect_response.strip().strip('`')
                correct_response = correct_response.strip().strip('`')
                
                response_data.append({
                    'category': key,
                    'incorrect': incorrect_response,
                    'correct_or_feedback': correct_response,
                    'citations': None,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(key),
                })
            else:
                print(f"Warning: LLM output correction '{bullet}' does not contain ' -> ' character")
        
        elif key in ['marking', 'overall_comments']:
            response_data.append({
                'category': key,
                'incorrect': None,
                'correct_or_feedback': bullet,
                'citations': None,
                'start': None,
                'end': None,
                'colour': colour_dict.get(key),
            })
        
        else:
            print(f"Warning: Invalid key '{key}'")

    return response_data

for key, message in messages.items():
    formatted_output = format_output_new(output2[key], key) #, message)
    # formatted_output = format_outputa(output2[key], key) #, message)
    print(formatted_output)