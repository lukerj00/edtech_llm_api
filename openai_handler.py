# openai_handler.py

import os
from typing import Dict, Any, List
import openai
import json
import re

class OpenAIHandler:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI()

    def generate_feedback(self, assignment_id: str, assignment_title: str, question_id: str, question_title: str, subject: str, 
                          qualification: str, feedback_category: str, assistant_id: str, thread_id: str, submission: str, mark_scheme: str, 
                          max_completion_tokens: int, temperature: float) -> Dict[str, Any]:
        
        if not thread_id and not assistant_id:
            assistant = self._get_or_create_assistant(assignment_id, assignment_title, question_id, question_title, subject, qualification, feedback_category, mark_scheme, temperature)
            thread, submission = self._init_thread(submission, assistant.id, question_title, max_completion_tokens, temperature)
            assistant_id, thread_id = assistant.id, thread.id
        try:
            # feedback = []
            # for category, message in self._get_feedback_messages(qualification, subject).items():
            message = self._get_category_message(feedback_category, qualification, subject)
            run = self._create_and_poll_run(thread_id, assistant_id, message, max_completion_tokens, temperature)
            print(f'{feedback_category} query status:', run.status)
            output = self._get_run_output(thread_id, run.id)
            print('output obtained', type(output), output)
            formatted_output = self._format_category_output(output, feedback_category, submission)
            print('formatted_output obtained:', type(formatted_output), formatted_output)
            # feedback.extend(formatted_output)

            print('returning feedback:', type(formatted_output))
            
            return {
                "status": run.status, 
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "submission": submission,
                "feedback": formatted_output
                }
        
        except openai.OpenAIError as e:
            raise ValueError(f"OpenAI API error: {str(e)}")


    def _get_or_create_assistant(self, assignment_id: str, assignment_title: str, question_id: str, question_title: str, subject: str, 
                                 qualification: str, feedback_category: str, mark_scheme: str, temperature: float):
        assistant_name = f"marking-assistant-a{assignment_id}-q{question_id}-c{feedback_category}"
        if os.path.isfile(mark_scheme):
            print('ms = file')
        else:
            print('ms = string')
        try:
            assistant = next((a for a in self.client.beta.assistants.list() if a.name == assistant_name), None)
            if assistant:
                print('assistant exists:', assistant.name)
                return assistant
        except openai.OpenAIError as e:
            print('error:', e)
            print('assistant does not exist')
            pass

        # create new assistant if doesn't exist
        vector_store = self._create_vector_store(assignment_id, question_id, mark_scheme)
        print('assistant temp=', temperature)
        assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=f"""You are an expert educational assessor for {qualification}-level {subject} - give accurate and extensive feedback for questions from the following assignment, entitled '{assignment_title}', carefully taking in to account the mark scheme provided where necessary.
                        Break down your feedback in to categories, giving only feedback for that category and listing your comments as bullet points under that category's title, in the exact following JSON format:
                        {{
                            "<feedback category>": [
                                "- `correction 1`", 
                                "- `correction 2`", 
                                "- `correction 3`",
                                "- ...",
                                "- ..."
                            ],
                        }}
                        It is very important that you enclose each correction in backticks within the JSON output.
                        Do NOT write anything in your reply outside of this JSON, and make sure you always using double quotation marks "" for each key or value string, and single quotation marks '' for punctuation ONLY.
                        """,
            model="gpt-4o",
            temperature=temperature,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
        )
        print('assistant created:', assistant.name, 'vector store:', vector_store.name)
        # # update assistant with vector store
        # assistant = self.client.beta.assistants.update(
        #     assistant_id=assistant.id,
        #     tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        # )
        return assistant

    def _create_vector_store(self, assignment_id: str, question_id: str, mark_scheme: str):
        vector_store_name = f"vector-store-a{assignment_id}-q{question_id}"
        vector_store = self.client.beta.vector_stores.create(name=vector_store_name)
        with open(mark_scheme, "rb") as file_stream:
            self.client.beta.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_stream,
            )
        return vector_store

    def _init_thread(self, submission: str, assistant_id: str, question_title: str, max_completion_tokens: int, temperature: float):
        # if submission and submission.startswith('@'):
        #     file_path = submission[1:]
        if os.path.isfile(submission): # file_path
            print('submission = file')
            try:
                submission_file = self.client.files.create(
                    file=open(submission, "rb"), purpose="assistants"
                )
                initial_message = {
                    "role": "user",
                    "content": f"""Student submission is attached below, for the question '{question_title}'. Please start by transcribing it EXACTLY to text and returning it as a string.
                    It is important that the string representation is as accurate and faithful as possible.
                    Give ONLY the final transcribed submission in your response below (no extra text before and after).
                    For this transciption only, the response does not have to be a JSON.""",                    
                    "attachments": [
                        {"file_id": submission_file.id, "tools": [{"type": "file_search"}]}
                    ],
                }
                # transcribe_message = {
                #     "role": "user",
                #     "content": """Please start by transcribing it EXACTLY to text and returning it as a string.
                #     It is important that the string representation is as accurate and faithful as possible.""",
                # }
                thread = self.client.beta.threads.create(messages=[initial_message])
                run = self.client.beta.threads.runs.create_and_poll(thread_id=thread.id,
                                                                    assistant_id=assistant_id,
                                                                    max_completion_tokens=max_completion_tokens,
                                                                    temperature=temperature
                                                                    )
                submission = self._get_run_output(thread.id, run.id)
                print('unformatted submission:\n', submission)
                submission = self._format_string(submission)
                print('formatted submission:\n', type(submission), submission, "\nsub_string_ended")
            except Exception as e:
                return f'Error processing file: {str(e)}'
        # else:
        #     return 'File not found on the server'
        else:
            print('submission = string')
            initial_message = {
                "role": "user",
                "content": f"Student submission is below, for the question '{question_title}':\n{submission}",
            }
            thread = self.client.beta.threads.create(messages=[initial_message])
        return thread, submission

    def _get_category_message(self, feedback_category: str, qualification: str, subject: str) -> Dict[str, Dict[str, str]]:
        return {
            "SPaG": {
                'role': 'user',
                'content': f"""
                1. Spelling, Punctuation and Grammar: give corrections for poor spelling, punctuation and grammar, bullet pointed in the exact following format: `- incorrect word\phrase -> correct word/phrase`. 
                Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                It is VERY important you ONLY reference incorrect words/passages EXACTLY as they occured in the student's submission.
                Give as many corrections as necessary (but only one point per correction even if the error occurs multiple times), appropriate for a student of {qualification}-level {subject}.
                """,
            },
            "historical_accuracy": {
                'role': 'user',
                'content': f"""
                2. Historical Accuracy and Analysis of Cause and Effect: give corrections for any errors in historical accuracy, time period awareness or logical analysis of cause and effect, bullet pointed in the exact following format: `- incorrect fact/logic -> correct fact/logic`.
                Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                It is VERY important you ONLY refer incorrect words/passages EXACTLY as they occured in the student's submission.
                Give as many corrections as necessary, appropriate for a student of {qualification}-level {subject}.
                """,
            },
            "overall_comments": {
                'role': 'user',
                'content': f"""
                3. Overall Comments and Areas for Improvement: give overall comments and suggestions for how the student could improve their work, bullet pointed in the exact following format: `- suggestion`.
                Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                """,
            },
            "marking": {
                'role': 'user',
                'content': f"""
                4. Marking: give estimated marks - carefully and extensively taking into account the mark scheme provided in your vector store - bullet pointed in the exact following format: `- marking feedback comment`.
                Give feedback only in the EXACT bullet-point JSON format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                """,
            },
        }[feedback_category]

    def _create_and_poll_run(self, thread_id: str, assistant_id: str, message: Dict[str, str], max_completion_tokens: int, temperature: float):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=message['role'],
            content=message['content'],
        )
        return self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id, 
            assistant_id=assistant_id,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature
        )

    def _format_string(self, text):
        # replace single newlines with empty string
        text = re.sub(r'(?<!\n)\n(?!\n)', '', text)
        # replace multiple newlines with one less
        text = re.sub(r'\n{2,}', lambda m: '\n' * (len(m.group()) - 1), text)
        return text

    def _get_run_output(self, thread_id: str, run_id: str):
        messages = self.client.beta.threads.messages.list(thread_id=thread_id, run_id=run_id)
        return messages.data[0].content[0].text.value if messages.data else ""

    def _format_category_output(self, output: str, category: str, submission: str) -> List[Dict[str, Any]]:
        colour_dict = {
            "SPaG": ["FFBF00", "EC4E02"],
            "historical_accuracy": ["02FFFF", "163E64"],
            "overall_comments": ["02FF5A", "12501B"],
            "marking": ["FF4CFE", "501649"],
        }
        # remove code block markers if present
        json_content = re.sub(r'```json\s*|\s*```', '', output.strip())
        # replace single quotes with double quotes for keys/string values
        json_content = re.sub(r'(^|[,{\[]\s*)\'(?=\S)|(?<=\S)\'(\s*[,}\]]|$)', '"', json_content)
        # remove trailing commas if present
        json_content = re.sub(r',\s*}', '}', json_content)
        json_content = re.sub(r',\s*]', ']', json_content)
        ###
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Problematic JSON content: {json_content}")
            
            # if parsing fails try  ast.literal_eval as a fallback
            try:
                import ast
                data = ast.literal_eval(json_content)
            except:
                print("Failed to parse JSON.")
                return None

        # extract list of bullets from output and iterate through
        json_key = list(data.keys())[0]
        bullets = data[json_key]
        # print('bullets=', bullets)
        response_data = []
        unique_parts = set()
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
            if category in ['SPaG', 'historical_accuracy']:###
                parts = re.split(r' -> ', bullet, maxsplit=1)
                
                if len(parts) == 2:
                    incorrect_response, correct_response = parts
                    incorrect_response = incorrect_response.strip().strip('`').strip('...').strip("'")
                    correct_response = correct_response.strip().strip('`').strip('...').strip("'")
                    parts = (incorrect_response, correct_response)
                    if parts not in unique_parts:
                        print(parts, 'not in unique_parts')
                        unique_parts.add(parts)
                        start_indices = [match.start() for match in re.finditer(re.escape(parts[0]), submission, re.IGNORECASE)]
                        end_indices = [ind + len(parts[0]) for ind in start_indices]   
                        unique_pairs = set()
                        for start_index, end_index in zip(start_indices, end_indices):  
                            pair = (start_index, end_index)
                            if pair not in unique_pairs:
                                unique_pairs.add(pair)          
                                response_data.append({
                                    'category': category,
                                    'incorrect_or_highlight': parts[0],
                                    'correct_or_feedback': parts[1],
                                    'citations': citations,
                                    'start': pair[0],
                                    'end': pair[1],
                                    'background_colour': colour_dict.get(category)[0],
                                    'text_colour': colour_dict.get(category)[1],
                                })
                            else:
                                print(pair, 'already in unique_pairs')
                    else:
                        print(parts, 'already in unique_parts')
                else:
                    print(f"Warning: LLM output correction '{bullet}' does not contain ' -> ' character")
            
            elif category in ['marking', 'overall_comments']:###
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