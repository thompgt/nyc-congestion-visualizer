import streamlit as st
from agents.llm_vis_agent import VisQueryAgent

# Create an instance of the Visualization agent
agent = VisQueryAgent()

def render_visualization_component():
    # Section header and instructions
    st.subheader("📊 Data Visualization")
    st.markdown("The code must generate a figure `fig` using Plotly.")

    # If AI previously generated visualization code, prefill it into the text box
    if "pending_ai_vis_code" in st.session_state:
        st.session_state.vis_code_input = st.session_state.pending_ai_vis_code
        del st.session_state.pending_ai_vis_code

    # Text area where user enters (or AI generates) visualization code
    vis_code = st.text_area(
        "Python code to visualize the dataset (>> for AI-generation)",
        height=300,
        key="vis_code_input"
    )

    # Initialize our figure
    fig = None

    # Add some spacing
    col1, col2, col3, col4 = st.columns([1, 1, 1, 5])

    # Execute button
    with col1:
        if st.button("Execute", use_container_width=True):
            try:
                # If prefixed with '>>', use the LLM to generate Plotly visualization code
                if vis_code.startswith(">>"):
                    with st.spinner("Processing..."):
                        vis_code = agent.run(vis_code, st.session_state.filtered_df)
                    st.session_state.pending_ai_vis_code = vis_code
                    st.rerun()

                # Otherwise, execute the user-supplied Python visualization code
                else:
                    local_vars = {"filtered_df": st.session_state.filtered_df.copy()}
                    exec(st.session_state.vis_code_input, {}, local_vars)

                    # Look for a Plotly figure named `fig` in the local execution context
                    fig = local_vars.get("fig")
                    if not fig:
                        st.warning("No Plotly figure `fig` found in the generated code.")
            except Exception as e:
                st.error(f"Error executing code: {e}")

    # Placeholder columns for spacing/alignment (unused)
    with col2:
        pass

    with col3:
        pass

    with col4:
        pass

    # Render the interactive chart in Streamlit
    if fig:
        st.plotly_chart(fig, use_container_width=True)
