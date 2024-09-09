import os
from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
import json
import re

class FeedbackItem(BaseModel):
    category: str = Field(description="The category of the feedback")
    incorrect_or_highlight: str = Field(description="The incorrect text or highlighted portion")
    correct_or_feedback: str = Field(description="The corrected text or feedback")
    citations: str = Field(description="Any citations or references")
    start: List[int] = Field(description="List of start indices in the original text")
    end: List[int] = Field(description="List of end indices in the original text")
    colour: str = Field(description="The color associated with this feedback category")

class OpenAIHandler:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
        self.embeddings = OpenAIEmbeddings()

    def generate_feedback(self, assignment_id: str, assignment_title: str, question_id: str, question_title: str, subject: str, 
                          qualification: str, submission: str, mark_scheme: str, 
                          max_completion_tokens: int, temperature: float) -> Dict[str, Any]:
        
        # Create vector store from mark scheme
        loader = TextLoader(mark_scheme)
        documents = loader.load()
        vector_store = FAISS.from_documents(documents, self.embeddings)

        # Initialize chat history
        chat_history = [
            SystemMessage(content=f"""You are an expert educational assessor for {qualification}-level {subject} - give accurate and extensive feedback for questions from the following assignment, entitled '{assignment_title}', carefully taking in to account the mark scheme provided where necessary.
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
                        """),
            HumanMessage(content=f"Student submission for the question '{question_title}':\n{submission}")
        ]

        feedback = []
        for category, prompt in self._get_feedback_prompts(qualification, subject).items():
            output_parser = PydanticOutputParser(pydantic_object=FeedbackItem)
            format_instructions = output_parser.get_format_instructions()

            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", prompt),
                ("human", "{format_instructions}\n\nPlease provide feedback for the following category: {category}")
            ])

            chat_prompt_with_values = chat_prompt.format_prompt(
                format_instructions=format_instructions,
                category=category
            )

            # Get relevant context from vector store
            relevant_docs = vector_store.similarity_search(chat_prompt_with_values.to_string(), k=2)
            relevant_context = "\n".join([doc.page_content for doc in relevant_docs])

            # Add relevant context to the chat history
            chat_history.append(HumanMessage(content=f"Relevant context from mark scheme:\n{relevant_context}"))
            chat_history.append(HumanMessage(content=chat_prompt_with_values.to_string()))

            # Get model response
            response = self.llm(chat_history)

            # Parse the response
            try:
                parsed_response = output_parser.parse(response.content)
                feedback.append(parsed_response.dict())
            except Exception as e:
                print(f"Error parsing response for category {category}: {e}")
                print(f"Raw response: {response.content}")

            # Remove the last two messages (context and prompt) to keep the history clean
            chat_history = chat_history[:-2]

        return {
            "status": "completed",
            "submission": submission,
            "feedback": feedback
        }

    def _get_feedback_prompts(self, qualification: str, subject: str) -> Dict[str, str]:
        return {
            "SPaG": f"Provide feedback on Spelling, Punctuation and Grammar for a {qualification}-level {subject} student.",
            "historical_accuracy": f"Provide feedback on Historical Accuracy and Analysis of Cause and Effect for a {qualification}-level {subject} student.",
            "overall_comments": f"Provide Overall Comments and Areas for Improvement for a {qualification}-level {subject} student.",
            "marking": f"Provide Marking feedback, taking into account the mark scheme, for a {qualification}-level {subject} student."
        }

    def _format_string(self, text):
        text = re.sub(r'(?<!\n)\n(?!\n)', '', text)
        text = re.sub(r'\n{2,}', lambda m: '\n' * (len(m.group()) - 1), text)
        return text