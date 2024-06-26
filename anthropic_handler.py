# anthropic_handler.py

import os
from typing import Dict, Any, List
import anthropic
import base64
import mimetypes
import json
import re
from pdf2image import convert_from_path
from PIL import Image

class AnthropicHandler:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ['ANTHROPIC_API_KEY']
        )
    
    def generate_feedback(self, assignment_id: str, assignment_title: str, subject: str, 
                          qualification: str, submission: str, mark_scheme: str, 
                          max_completion_tokens: int, temperature: float) -> Dict[str, Any]:
        try:
            mark_scheme_payload = self._process_mark_scheme(mark_scheme)
            print('mark scheme payload obtained')
            messages = self._get_initial_messages(assignment_title, subject, qualification, submission, mark_scheme_payload, max_completion_tokens)
            print('initial messages obtained')
            # print('messages:', type(messages), len(messages), messages[-1])
            
            feedback = []
            for category, input_message in self._get_feedback_messages(qualification, subject).items():
                messages += [input_message]
                # print('messages:', type(messages), len(messages), messages[-1])
                output_message = self._get_run_output(messages, max_completion_tokens, temperature)
                print('output_message:', type(output_message), output_message)
                messages += [output_message]
                print('output message type=',type(output_message),'category type=',type(category),'submission=',type(submission))
                formatted_output = self._format_category_output(output_message, category, submission)
                # print('formatted_output:', type(formatted_output), formatted_output)
                feedback.extend(formatted_output)

            return {
                "status": "completed", 
                "submission": submission,
                "feedback": feedback
                }

        except anthropic.AnthropicError as e:
            raise ValueError(f"Anthropic API error: {str(e)}")
        
    def _process_mark_scheme(self, mark_scheme):
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        _, file_extension = os.path.splitext(mark_scheme)
        file_extension = file_extension.lower()
        if file_extension in image_extensions:
            pass
        elif file_extension == '.pdf':
            ms_name = os.path.splitext(os.path.basename(mark_scheme))[0]
            images = convert_from_path(mark_scheme)
            output_dir = os.path.dirname(mark_scheme)
            mark_scheme = os.path.join(output_dir, f'{ms_name}.png')
            images[0].save(mark_scheme, 'PNG')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        if not os.path.exists(mark_scheme):
            raise FileNotFoundError(f"File not found: {mark_scheme}")
        with open(mark_scheme, 'rb') as file:
            ms_content = file.read()
        base64_encoded = base64.b64encode(ms_content).decode('utf-8')
        media_type, _ = mimetypes.guess_type(mark_scheme)
        if media_type is None:
            media_type = 'application/octet-stream'
        return {
                "type": "base64",
                "media_type": media_type,
                "data": base64_encoded
            }
        
    def _get_initial_messages(self, assignment_title: str, subject: str, qualification: str, submission: str, mark_scheme_payload: Dict[str, Any], max_completion_tokens: int):
        instructions = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""You are an expert educational assessor for {qualification}-level {subject} - give accurate and extensive feedback on the following assignment, entitled '{assignment_title}', carefully taking in to account the mark scheme provided, where necessary.
                        Break down your feedback in to categories, giving only feedback for that category and listing your comments as bullet points under that category's title, in the exact following JSON format:
                        {{
                            "<feedback category>": [
                                "- correction 1", 
                                "- correction 2", 
                                "- correction 3",
                                "- ...",
                                "- ..."
                            ],
                        }}
                        Do NOT write anything in your reply outside of this JSON, and make sure you always using double quotation marks "" for each key or value string, and single quotation marks '' for punctuation ONLY.
                        """,
                }
            ]
        }
        submission_and_ms = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""The user's submission is below:
                        {submission}
                        and the mark scheme is attached to this message. 
                        Parse these both and await further instructions regarding the feedback categories required.
                        """
                },
                {
                    "type": "image",
                    "source": mark_scheme_payload
                }
            ]
        }
        return [
            instructions,
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Thank you for the instructions. I will await the submission and mark scheme and then do my best to provide accurate feedback based on the categories requested."
                    }
                ]
            },
            submission_and_ms,
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have received the submission and mark scheme. I will now begin to provide feedback based on the categories requested, following the preceding instructions."
                    }
                ]
            }
        ]

    def _get_feedback_messages(self, qualification: str, subject: str) -> Dict[str, Dict[str, str]]:
        return {
            "SPaG": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        1. Spelling, Punctuation and Grammar: give corrections for poor spelling, punctuation and grammar, bullet pointed in the exact following format: `- incorrect word\phrase -> correct word/phrase`. 
                        Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                        Specifically, use the following JSON structure for this category:
                        "Spelling, Punctuation and Grammar": {{
                            [
                                "- incorrect word/phrase -> correct word/phrase", 
                                "- ...", 
                                "- ...",
                                "- ...",
                                "- ..."
                            ]
                        }}
                        It is VERY important you ONLY reference incorrect words/passages EXACTLY as they occured in the student's submission.
                        Give as many corrections as necessary (but only one point per correction even if the error occurs multiple times), appropriate for a student of {qualification}-level {subject}.
                        """
                    }
                ]
            },
            "historical_accuracy": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        2. Historical Accuracy and Analysis of Cause and Effect: give corrections for any errors in historical accuracy, time period awareness or logical analysis of cause and effect, bullet pointed in the exact following format: `- incorrect fact/logic -> correct fact/logic`.
                        Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                        Specifically, use the following JSON structure for this category:
                        "Historical Accuracy and Analysis of Cause and Effect": {{
                            [
                                "- incorrect fact/logic -> correct fact/logic", 
                                "- ...", 
                                "- ...",
                                "- ...",
                                "- ..."
                            ]
                        }}
                        It is VERY important you ONLY refer incorrect words/passages EXACTLY as they occured in the student's submission.
                        Give as many corrections as necessary, appropriate for a student of {qualification}-level {subject}.
                        """
                    }
                ]
            },
            "overall_comments": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        3. Overall Comments and Areas for Improvement: give overall comments and suggestions for how the student could improve their work, bullet pointed in the exact following format: `- suggestion`.
                        Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                        Specifically, use the following JSON structure for this category:
                        "Overall Comments": {{
                            [
                                "- positive comment or suggestion for improvement", 
                                "- ...", 
                                "- ...",
                                "- ...",
                                "- ..."
                            ]
                        }}
                        Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                        """
                    }
                ]
            },
            "marking": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        4. Marking: give estimated marks - carefully and extensively taking into account the mark scheme provided in your vector store - bullet pointed in the exact following format: `- marking feedback comment`.
                        Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                        Specifically, use the following JSON structure for this category:
                        "Overall Comments": {{
                            [
                                "- marking feedback comment", 
                                "- ...", 
                                "- ...",
                                "- ...",
                                "- ..."
                            ]
                        }}
                        Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                        """
                    }
                ]
            }
        }
    
    def _get_run_output(self, messages, max_completion_tokens, temperature):
        message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=max_completion_tokens,
                messages=messages,
                temperature=temperature
                )
        return {
            "role": "assistant",
            "content": message.content
        }            
            
    
    def _format_category_output(self, output_message, category, submission) -> List[Dict[str, Any]]:
        colour_dict = {
            "SPaG": "orange",
            "historical_accuracy": "blue",
            "overall_comments": "green",
            "marking": "purple",
        }
        try:
            data = json.loads(output_message["content"][0].text)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Problematic JSON content: {output_message}")

            try:
                import ast
                data = ast.literal_eval(output_message)
            except:
                print("Failed to parse JSON.")
                return None
            
        # extract list of bullets from output and iterate through
        json_key = list(data.keys())[0]
        bullets = data[json_key]
        # print('bullets=', bullets)
        response_data = []
        for bullet in bullets:
            bullet = bullet.strip('- ').strip()

            pattern = r'【([^】]+)】'
            match = re.search(pattern, bullet)
            if match:
                citations = match.group(1)
                bullet = re.sub(pattern, '', bullet).strip()
            else:
                citations = None
            
            # assemble JSON response for each bullet, noting categories are handled differently based on if the output must be split into parts
            if category in ['SPaG', 'historical_accuracy']:
                parts = re.split(r' -> ', bullet, maxsplit=1)
                if len(parts) == 2:
                    incorrect_response, correct_response = parts
                    incorrect_response = incorrect_response.strip().strip('`').strip('...').strip("'")
                    correct_response = correct_response.strip().strip('`').strip('...').strip("'")
                    if os.path.isfile(submission):
                        start_indices, end_indices = None, None
                    else:
                        start_indices = [match.start() for match in re.finditer(re.escape(incorrect_response), submission, re.IGNORECASE)]
                        end_indices = [ind + len(incorrect_response) for ind in start_indices]                 
                    
                    response_data.append({
                        'category': category,
                        'incorrect_or_highlight': incorrect_response,
                        'correct_or_feedback': correct_response,
                        'citations': citations,
                        'start': start_indices,
                        'end': end_indices,
                        'colour': colour_dict.get(category),
                    })
                else:
                    print(f"Warning: LLM output correction '{bullet}' does not contain ' -> ' character")
            
            elif category in ['marking', 'overall_comments']:
                bullet = bullet.strip().strip('`').strip('...')
                response_data.append({
                    'category': category,
                    'incorrect_or_highlight': None,
                    'correct_or_feedback': bullet,
                    'citations': citations,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(category),
                })
            
            else:
                print(f"Warning: Invalid category '{category}'")

        return response_data