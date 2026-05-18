import streamlit as st
from utils.data import load_data
from agents.llm_pandas_agent import PandasQueryAgent

# Create an instance of the pandas agent
agent = PandasQueryAgent()

def render_pandas_component():
    # Section header and usage instructions
    st.subheader("🔎 Pandas filter query")
    st.markdown("Example: `filtered_df = filtered_df[filtered_df['Vehicle Class'] == '1 - Cars, Pickups and Vans']`")

    # If AI previously generated code, prefill it into the text area
    if "pending_ai_code" in st.session_state:
        st.session_state.code_input = st.session_state.pending_ai_code
        del st.session_state.pending_ai_code

    # Text area for manual or AI-generated pandas code input
    user_code = st.text_area(
        "Python code to run on the dataset (>> for AI-generation)",
        height=300,
        key="code_input"
    )

    # Create layout with 3 action buttons and some space
    col1, col2, col3, col4 = st.columns([1, 1, 1, 5])

    # Execute button
    with col1:
        if st.button("Execute", use_container_width=True):
            try:
                if user_code.startswith(">>"):
                    # If prefixed with '>>', use LLM to generate pandas code
                    with st.spinner("Processing..."):
                        pandas_query = agent.run(user_code[2:], st.session_state.filtered_df)
                    st.session_state.pending_ai_code = pandas_query
                    st.rerun()

                else:
                    # Manual code execution: run user-supplied code on a local copy of the dataframe
                    local_vars = {"filtered_df": st.session_state.filtered_df.copy()}
                    exec(user_code, {}, local_vars)

                    # Only update session state if the result is a valid filtered DataFrame
                    if "filtered_df" in local_vars:
                        # Add current state to history (for undo)
                        st.session_state.df_history.append(st.session_state.filtered_df.copy())

                        # Cap history to last 5 states
                        if len(st.session_state.df_history) > 5:
                            st.session_state.df_history.pop(0)

                        # Update the filtered dataframe in session state
                        st.session_state.filtered_df = local_vars["filtered_df"]
                        st.rerun()
                    else:
                        st.warning("Please assign the result to `filtered_df`.")
            except Exception as e:
                st.error(f"Error executing code: {e}")

    # Undo button
    with col2:
        if st.button("Undo", use_container_width=True):
            if st.session_state.df_history:
                # Revert to previous version of the filtered DataFrame
                st.session_state.filtered_df = st.session_state.df_history.pop()
                st.success("Reverted to previous filter.")
                st.rerun()
            else:
                st.warning("No previous state to undo.")

    # Reset button
    with col3:
        if st.button("Reset", use_container_width=True):
            # Reload the original dataset and clear history
            st.session_state.filtered_df = load_data()
            st.session_state.df_history = []
            st.success("Reset to original dataset.")
            st.rerun()

            # Reset agent history
            agent._reset_chat()

    # Placeholder column for spacing/alignment (unused)
    with col4:
        pass
