import openai
from app.config import get_settings
from typing import List, Dict, Optional
import json

settings = get_settings()


class LLMService:
    """Large Language Model service for conversation and correction using OpenRouter GPT-5"""

    def __init__(self):
        # OpenRouter client with GPT-5-chat
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )
        self.system_prompt = """You are an experienced English teacher helping Korean students learn English through conversation.

Your role:
1. Have natural, engaging conversations with students
2. Adapt your language level to the student's proficiency
3. Gently correct grammar and pronunciation errors
4. Suggest more natural expressions when appropriate
5. Be encouraging and supportive

When responding:
- Keep responses conversational and natural
- Use clear, simple English for beginners
- Provide corrections in a helpful, non-judgmental way
- Suggest better expressions when relevant
"""

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a response to the user's message using GPT-5-chat

        Args:
            user_message: User's input text
            conversation_history: Previous conversation messages

        Returns:
            Assistant's response
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="openai/gpt-5-chat",
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                extra_headers={
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                }
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error in LLM service: {e}")
            return "I'm sorry, I couldn't process that. Could you please try again?"

    async def analyze_and_correct(self, user_text: str) -> Dict:
        """
        Analyze user's text for grammar, vocabulary, and pronunciation issues using GPT-5

        Args:
            user_text: User's input text

        Returns:
            Dictionary containing corrections and suggestions
        """
        try:
            correction_prompt = f"""Analyze this English sentence from a Korean learner and provide corrections:

Sentence: "{user_text}"

Provide a JSON response with:
1. "has_errors": boolean
2. "corrections": array of objects with:
   - "type": "grammar" | "vocabulary" | "expression"
   - "original": the incorrect part
   - "corrected": the correct version
   - "explanation": brief explanation in Korean
   - "severity": "low" | "medium" | "high"
3. "better_expression": a more natural way to say the same thing (if applicable)
4. "overall_feedback": brief encouraging feedback in Korean

Return only valid JSON."""

            response = self.client.chat.completions.create(
                model="openai/gpt-5-chat",
                messages=[
                    {"role": "system", "content": "You are an English grammar and expression expert."},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                extra_headers={
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                }
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in correction analysis: {e}")
            return {
                "has_errors": False,
                "corrections": [],
                "better_expression": None,
                "overall_feedback": "분석 중 오류가 발생했습니다."
            }

    async def generate_conversation_starter(self, difficulty: str = "beginner") -> str:
        """
        Generate a conversation starter based on difficulty level using GPT-5

        Args:
            difficulty: "beginner", "intermediate", or "advanced"

        Returns:
            Conversation starter text
        """
        try:
            prompt = f"""Generate a natural conversation starter for a {difficulty} level English learner.
The topic should be casual and everyday. Keep it simple and friendly.
Just return the conversation starter, nothing else."""

            response = self.client.chat.completions.create(
                model="openai/gpt-5-chat",
                messages=[
                    {"role": "system", "content": "You are a friendly English teacher."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100,
                extra_headers={
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                }
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating conversation starter: {e}")
            return "Hello! How are you doing today?"
