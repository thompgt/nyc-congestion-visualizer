import streamlit as st
from agents.llm_qna_agent import QnaQueryAgent

# Create an instance of the QnA agent
agent = QnaQueryAgent()

def render_qna_component():
    st.subheader("❓ Q & A About the Dataset")
    st.markdown("Ask general questions about the data.")

    user_question = st.text_area("Your question", key="qna_input", height=300)

    # If user has asked before, persist the answer
    if "qna_answer" in st.session_state:
        st.markdown("**Answer:**")
        st.write(st.session_state.qna_answer)

    # Add some spacing
    col1, col2, col3, col4 = st.columns([1, 1, 1, 5])

    with col1:
        if st.button("Ask", use_container_width=True):
            try:
                with st.spinner("Processing..."):
                    answer = agent.run(user_question, st.session_state.filtered_df)
                st.session_state.qna_answer = answer
                st.rerun()
            except Exception as e:
                st.error(f"Error answering question: {e}")

    # Placeholder columns for spacing/alignment (unused)
    with col2:
        pass

    with col3:
        pass

    with col4:
        pass
