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

    def generate_feedback(self, assignment_id: str, assignment_title: str, subject: str, 
                          qualification: str, submission: str, mark_scheme: str, 
                          max_completion_tokens: int, temperature: float) -> Dict[str, Any]:
        try:
            assistant = self._get_or_create_assistant(assignment_id, assignment_title, subject, qualification, mark_scheme, temperature)
            thread = self._create_thread(submission)
            
            corrections = []
            for category, message in self._get_feedback_messages(qualification, subject).items():
                run = self._create_and_poll_run(thread.id, assistant.id, message, max_completion_tokens)
                print(f'{category} query status:', run.status)
                output = self._get_run_output(thread.id, run.id)
                # print('output:', type(output), output)
                formatted_output = self._format_category_output(output, category, submission)
                # print('formatted_output:', type(formatted_output), formatted_output)
                corrections.extend(formatted_output)
            
            return {"status": run.status, "corrections": corrections}
        
        except openai.OpenAIError as e:
            raise ValueError(f"OpenAI API error: {str(e)}")

    def _get_or_create_assistant(self, assignment_id: str, assignment_title: str, subject: str, 
                                 qualification: str, mark_scheme: str, temperature: float):
        assistant_name = f"marking-assistant-{assignment_id}"
        try:
            assistant = next((a for a in self.client.beta.assistants.list() if a.name == assistant_name), None)
            if assistant:
                print('assistant exists:', assistant.name)
                return assistant
        except openai.OpenAIError:
            print('assistant does not exist')
            pass

        # create new assistant if doesn't exist
        vector_store = self._create_vector_store(assignment_id, mark_scheme)
        assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=f"""You are an expert educational assessor for {qualification}-level {subject} - give accurate and extensive feedback on the following assignment, entitled '{assignment_title}', carefully taking in to account the mark scheme provided, where necessary.
                        Break down your feedback in to categories, giving only feedback for that category and listing your comments as bullet points under that category's title, in the following exact JSON format:
                        {{
                            "<category>": [
                                "- `correction 1`", 
                                "- `correction 2`", 
                                "- `correction 3`",
                                "- ...",
                                "- ..."
                            ],
                        }}
                        It is very important that you enclose each correction in backticks.
                        It is also very important that you always using double quotation marks "" for each key or value string, and single quotation marks '' for punctuation ONLY.
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

    def _create_vector_store(self, assignment_id: str, mark_scheme: str):
        vector_store_name = f"vector-store-{assignment_id}"
        vector_store = self.client.beta.vector_stores.create(name=vector_store_name)
        with open(mark_scheme, "rb") as file_stream:
            self.client.beta.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_stream,
            )
        return vector_store

    def _create_thread(self, submission: str):
        if os.path.isfile(submission):
            submission_file = self.client.files.create(
                file=open(submission, "rb"), purpose="assistants"
            )
            initial_message = {
                "role": "user",
                "content": "Student submission (see attached):",
                "attachments": [
                    {"file_id": submission_file.id, "tools": [{"type": "file_search"}]}
                ],
            }
        else:
            initial_message = {
                "role": "user",
                "content": f"Student submission:\n{submission}",
            }
        return self.client.beta.threads.create(messages=[initial_message])

    def _get_feedback_messages(self, qualification: str, subject: str) -> Dict[str, Dict[str, str]]:
        return {
            "SPaG": {
                'role': 'user',
                'content': f"""
                1. Spelling, Punctuation and Grammar: give corrections for poor spelling, punctuation and grammar, bullet pointed in the exact following format: `- incorrect word\phrase -> correct word/phrase`. 
                Give feedback only in the EXACT bullet-point format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                It is VERY important you ONLY reference incorrect words/passages EXACTLY as they occured in the student's submission.
                Give as many corrections as necessary (but only one point per correction even if the error occurs multiple times), appropriate for a student of {qualification}-level {subject}.
                """,
            },
            "historical_accuracy": {
                'role': 'user',
                'content': f"""
                2. Historical Accuracy and Analysis of Cause and Effect: give corrections for any errors in historical accuracy, time period awareness or logical analysis of cause and effect, bullet pointed in the exact following format: `- incorrect fact/logic -> correct fact/logic`.
                Give feedback only in the EXACT bullet-point format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                It is VERY important you ONLY refer incorrect words/passages EXACTLY as they occured in the student's submission.
                Give as many corrections as necessary, appropriate for a student of {qualification}-level {subject}.
                """,
            },
            "overall_comments": {
                'role': 'user',
                'content': f"""
                3. Overall Comments and Areas for Improvement: give overall comments and suggestions for how the student could improve their work, bullet pointed in the exact following format: `- suggestion`.
                Give feedback only in the EXACT bullet-point format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                """,
            },
            "marking": {
                'role': 'user',
                'content': f"""
                4. Marking: give estimated marks - carefully and extensively taking into account the mark scheme provided in your vector store - bullet pointed in the exact following format: `- marking feedback comment`.
                Give feedback only in the EXACT bullet-point format requested above, and only for the category stated (do NOT include any other feedback in addition to the bullet points of form described above).
                Give up to 3 comments, appropriate for a student of {qualification}-level {subject} and addressed in first person.
                """,
            },
        }

    def _create_and_poll_run(self, thread_id: str, assistant_id: str, message: Dict[str, str], max_completion_tokens: int):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=message['role'],
            content=message['content'],
        )
        return self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id, 
            assistant_id=assistant_id,
            max_completion_tokens=max_completion_tokens,
        )

    def _get_run_output(self, thread_id: str, run_id: str):
        messages = self.client.beta.threads.messages.list(thread_id=thread_id, run_id=run_id)
        return messages.data[0].content[0].text.value if messages.data else ""

    def _format_category_output(self, output: str, category: str, submission: str) -> List[Dict[str, Any]]:
        colour_dict = {
            "SPaG": "orange",
            "historical_accuracy": "blue",
            "overall_comments": "green",
            "marking": "purple",
        }

        # clean up the output JSON content
        json_content = output.strip('```json\n').strip()
        
        # replace erroneous single quotes delimiters with double quotes
        json_content = re.sub(r'(^|[,{\[]\s*)\'(?=\S)|(?<=\S)\'(\s*[,}\]]|$)', '"', json_content)

        # extract JSON
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error for key {category}: {e}")
            print(f"Problematic JSON content: {json_content}")
            return []

        # extract list of bullets from output and iterate through
        json_key = list(data.keys())[0]
        bullets = data[json_key]
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
                        'incorrect': incorrect_response,
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
                    'incorrect': None,
                    'correct_or_feedback': bullet,
                    'citations': citations,
                    'start': None,
                    'end': None,
                    'colour': colour_dict.get(category),
                })
            
            else:
                print(f"Warning: Invalid category '{category}'")

        return response_data
    