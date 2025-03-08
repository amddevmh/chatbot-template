#!/usr/bin/env python3
"""
Chat service to handle LLM interactions
"""
from openai import OpenAI, OpenAIError
from app.config import settings

class ChatService:
    """Service for interacting with an LLM provider"""
    
    def __init__(self):
        """Initialize the OpenAI client with settings"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
    
    async def get_chat_response(self, message: str) -> str:
        """
        Get a response from the LLM for a given message
        
        Args:
            message: The user's input message
            
        Returns:
            The LLM's response as a string
            
        Raises:
            OpenAIError: If the LLM request fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise Exception(f"LLM request failed: {str(e)}")