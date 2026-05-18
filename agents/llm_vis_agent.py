from agents.base_agent import LLMBaseAgent
import pandas as pd

class VisQueryAgent(LLMBaseAgent):
    def run(self, prompt: str, df: pd.DataFrame) -> str:
        # Prepare column context
        columns, snapshot, column_value_info = self._get_column_context(df)

        # Construct the system message for the LLM
        system_message = (
            "You are an assistant that generates Python visualization code using Plotly.\\n"
            "Use Plotly Express and set layout height to at least 600 pixels\\n"
			"If generating a density_mapbox, use the 'carto-positron' mapbox_style\\n"
            "The dataset will involve MTA congestion relief zones in NYC (beginning 2025).\\n"
            "Assume the DataFrame is named 'filtered_df'.\\n"
            "Your code MUST create a Plotly figure object named `fig`. Do not do fig.show() afterwards.\n"
            "Do not include print statements, markdown, or any explanations.\\n"
            "Only return executable Python code. Do not have any markdowns.\n"
            f"Column names: {columns}\\n"
        )

        if column_value_info:
            system_message += "\\nHere are example values for some columns:\\n" + column_value_info

        system_message += f"\\nData preview (first 5 rows):\\n{snapshot}\\n"

        # Call the model
        return self._call_openai(system_message, prompt, max_tokens=1000, temperature=0.2)