from agents.base_agent import LLMBaseAgent
import pandas as pd

class PandasQueryAgent(LLMBaseAgent):
    def run(self, prompt: str, df: pd.DataFrame) -> str:
        # Prepare column context
        columns, snapshot, column_value_info = self._get_column_context(df)

        # Construct the system message for the LLM
        system_message = (
            "You are an assistant that converts natural language queries into valid pandas DataFrame code.\\n"
            "The dataset will involve MTA congestion relief zones in NYC (beginning 2025).\\n"
            "When the query asks about regions / spatial distributions / heatmaps, you may likely need latitude / longitude information.\\n"
            "Assume the DataFrame is named 'filtered_df'.\\n"
            "You should ONLY return valid pandas code — no explanations, no markdown, no print statements, no other types of code.\\n"
            "If you are asked to do a complex task (like visualizing data), only provide the pandas code that will give the required data\\n"
            "Always assign the final result to a variable called 'filtered_df'.\\n"
            "⚠️ Your output MUST be a pandas DataFrame (not a Series, NumPy array, or scalar).\\n"
            "If the query results in a single column or value, wrap it as a DataFrame.\\n\\n"
            f"Column names: {columns}\\n"
        )

        if column_value_info:
            system_message += "\\nHere are example values for some columns:\\n" + column_value_info

        system_message += f"\\nData preview (first 5 rows):\\n{snapshot}\\n"

        # Call the model
        return self._call_openai(system_message, prompt, max_tokens=1000, temperature=0.2)