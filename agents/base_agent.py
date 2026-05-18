import os
import pandas as pd
from openai import OpenAI
from abc import ABC, abstractmethod

# Abstract base class for LLM-powered dataframe agents
class LLMBaseAgent(ABC):
    def __init__(self, model: str = "gpt-4o-mini", max_unique_values: int = 10):
        """
        Initialize the LLM base agent.

        Parameters:
        - model: The OpenAI model to use (default is 'gpt-4o-mini').
        - max_unique_values: Max number of unique values to include per categorical column.
        """
        self.model = model
        self.max_unique_values = max_unique_values
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_history = []

    def _reset_chat(self):
        self.chat_history = []

    def _get_column_context(self, df: pd.DataFrame) -> str:
        """
        Extract useful context from the DataFrame including:
        - List of column names
        - A snapshot of the first 5 rows
        - Example values from categorical columns (if cardinality is low)

        Returns:
        - Tuple of (columns list, preview string, formatted value info string)
        """
        columns = df.columns.tolist()
        snapshot = df.head(5).to_string(index=False)

        value_context = ""
        for col in df.columns:
            unique_vals = df[col].dropna().unique()
            # Include sample values only for low-cardinality categorical columns
            if df[col].dtype == object or df[col].dtype.name == "category":
                if len(unique_vals) <= self.max_unique_values:
                    formatted = ', '.join([f'"{str(v)}"' for v in sorted(unique_vals)])
                    value_context += f"- {col}: {formatted}\\n"

        return columns, snapshot, value_context

    def _call_openai(self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3
    ):
        """
        Send a structured prompt to OpenAI's chat model and return the raw LLM response string.

        Parameters:
        - system_message: Context to guide the assistant
        - user_prompt: The user’s question or instruction
        - max_tokens: Response length limit
        - temperature: Creativity of the response (0 = deterministic, 1 = creative)

        Returns:
        - The generated message content as a plain string
        """
        # Initialize chat history with system message if not yet started
        if not self.chat_history and system_message:
            self.chat_history.append({"role": "system", "content": system_message})
        if user_prompt:
            self.chat_history.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.chat_history,
            temperature=temperature,
            max_tokens=max_tokens
        )

        reply = response.choices[0].message.content.strip()
        self.chat_history.append({"role": "assistant", "content": reply})
        return reply

    @abstractmethod
    def run(self, prompt: str, df: pd.DataFrame) -> str:
        """
        Abstract method to be implemented by subclasses.
        It defines how to use the LLM to generate a result from the prompt and DataFrame.

        Parameters:
        - prompt: The user query
        - df: The dataframe to operate on

        Returns:
        - A string result (e.g. Python code, answer, etc.)
        """
        pass
