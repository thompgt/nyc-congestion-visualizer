from agents.base_agent import LLMBaseAgent
import pandas as pd

class QnaQueryAgent(LLMBaseAgent):
    def run(self, prompt: str, df: pd.DataFrame) -> str:
        # Prepare column context
        columns, snapshot, column_value_info = self._get_column_context(df)

        # Construct the system message for the LLM
        system_message = (
            "You are a data assistant that answers general questions about a pandas DataFrame.\\n"
            "The dataset will involve MTA congestion relief zones in NYC (beginning 2025).\n"
            "Respond using markdown.\\n"
            f"Columns: {columns}\\n"
        )

        if column_value_info:
            system_message += "\\nHere are example values for some columns:\\n" + column_value_info

        system_message += f"\\nData preview (first 5 rows):\\n{snapshot}\\n"

        # Call the model
        return self._call_openai(system_message, prompt, max_tokens=1000, temperature=0.2)