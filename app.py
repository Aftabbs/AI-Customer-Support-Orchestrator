import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import SupportOrchestrator


# Page configuration
st.set_page_config(
    page_title="AI Support Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .ticket-box {
        background-color: #f0f2f6;
        color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .response-box {
        background-color: #e8f4f8;
        color: #0e1117;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Ensure text in markdown is visible */
    .response-box p, .response-box div {
        color: #0e1117 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = SupportOrchestrator()
    if 'ticket_history' not in st.session_state:
        st.session_state.ticket_history = []


def render_header():
    """Render application header"""
    st.markdown('<div class="main-header">🤖 AI Customer Support Orchestrator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Multi-Agent System with Guardrails & Evaluation</div>',
        unsafe_allow_html=True
    )


def render_sidebar():
    """Render sidebar with information and controls"""
    with st.sidebar:
        st.header("📊 System Overview")

        st.markdown("""
        ### 🎯 Agent Types
        - **Classifier**: Categorizes tickets
        - **Technical**: Handles technical issues
        - **Billing**: Manages billing queries
        - **General**: Answers general questions

        ### 🛡️ Guardrails
        - Content filtering
        - Response validation
        - Escalation rules
        - Quality checks

        ### 📈 Evaluation
        - Response time tracking
        - Confidence scoring
        - Escalation monitoring
        - Performance metrics
        """)

        st.divider()

        # Example tickets
        st.subheader("💡 Example Tickets")

        example_tickets = {
            "Technical Issue": "My app crashes every time I try to upload a file. I'm using version 2.3.1 on Windows 11.",
            "Billing Question": "I was charged twice this month for my subscription. Can I get a refund for the duplicate charge?",
            "General Inquiry": "What are the main features of the premium plan? I'm considering upgrading.",
            "Escalation Test": "This is URGENT! I need an immediate refund of $5000 or I will contact my lawyer!"
        }

        for title, ticket in example_tickets.items():
            if st.button(f"📝 {title}", use_container_width=True):
                st.session_state.example_ticket = ticket


def render_ticket_input():
    """Render ticket input section"""
    st.header("📝 Submit Support Ticket")

    # Pre-fill if example selected
    default_text = st.session_state.get('example_ticket', '')

    ticket_text = st.text_area(
        "Enter your support ticket:",
        value=default_text,
        height=150,
        placeholder="Describe your issue or question here...",
        key="ticket_input"
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        submit_button = st.button("🚀 Submit Ticket", type="primary", use_container_width=True)

    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)

    if clear_button:
        st.session_state.example_ticket = ''
        st.rerun()

    return ticket_text, submit_button


def render_response(result):
    """Render agent response"""
    st.header("💬 Agent Response")

    # Response metadata
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Category", result['category'])

    with col2:
        confidence_color = "🟢" if result['confidence'] > 0.7 else "🟡" if result['confidence'] > 0.5 else "🔴"
        st.metric("Confidence", f"{confidence_color} {result['confidence']:.2%}")

    with col3:
        st.metric("Response Time", f"{result['metadata'].get('response_time', 0):.2f}s")

    with col4:
        escalation_status = "⚠️ YES" if result['escalated'] else "✅ NO"
        st.metric("Escalated", escalation_status)

    # Main response
    st.markdown("### Response:")
    st.markdown(
        f'<div class="response-box"><p style="color: #0e1117; margin: 0;">{result["response"]}</p></div>',
        unsafe_allow_html=True
    )

    # Additional details in expander
    with st.expander("🔍 View Details"):
        st.json({
            "Ticket ID": result['ticket_id'],
            "Agent Used": result['agent_used'],
            "Guardrail Violations": result['guardrail_violations'],
            "Metadata": result['metadata']
        })


def render_metrics():
    """Render metrics dashboard"""
    st.header("📊 Performance Metrics")

    metrics = st.session_state.orchestrator.get_metrics()

    if metrics['total_interactions'] == 0:
        st.info("No interactions yet. Submit a ticket to see metrics!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tickets", metrics['total_interactions'])

    with col2:
        st.metric("Avg Response Time", f"{metrics['avg_response_time']}s")

    with col3:
        st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1%}")

    with col4:
        st.metric("Escalation Rate", f"{metrics['escalation_rate']:.1%}")

    # Category breakdown
    if metrics.get('category_breakdown'):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Category Distribution")
            cat_df = pd.DataFrame(
                list(metrics['category_breakdown'].items()),
                columns=['Category', 'Count']
            )
            fig = px.pie(cat_df, values='Count', names='Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Agent Performance")
            agent_perf = metrics.get('agent_performance', {})
            if agent_perf:
                perf_data = []
                for agent, stats in agent_perf.items():
                    perf_data.append({
                        'Agent': agent,
                        'Tickets': stats['count'],
                        'Avg Confidence': round(stats['avg_confidence'], 3)
                    })
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, use_container_width=True, hide_index=True)

    # Export metrics
    if st.button("📥 Export Metrics"):
        st.session_state.orchestrator.export_metrics()
        st.success("Metrics exported to metrics_log.json")


def render_history():
    """Render ticket history"""
    if not st.session_state.ticket_history:
        return

    st.header("📜 Ticket History")

    for idx, item in enumerate(reversed(st.session_state.ticket_history[-5:])):
        with st.expander(f"🎫 {item['ticket_id']} - {item['category']} ({item['timestamp']})"):
            st.markdown(f"**Ticket:** {item['ticket']}")
            st.markdown(f"**Agent:** {item['agent_used']}")
            st.markdown(f"**Confidence:** {item['confidence']:.2%}")
            st.markdown(f"**Escalated:** {'Yes' if item['escalated'] else 'No'}")


def main():
    """Main application"""
    initialize_session_state()

    render_header()
    render_sidebar()

    # Main content
    ticket_text, submit_button = render_ticket_input()

    if submit_button and ticket_text.strip():
        with st.spinner("🤖 Processing your ticket..."):
            try:
                # Process ticket
                result = st.session_state.orchestrator.process_ticket(ticket_text)

                # Add to history
                st.session_state.ticket_history.append({
                    'ticket_id': result['ticket_id'],
                    'ticket': ticket_text,
                    'category': result['category'],
                    'agent_used': result['agent_used'],
                    'confidence': result['confidence'],
                    'escalated': result['escalated'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                # Render response
                render_response(result)

            except Exception as e:
                st.error(f"❌ Error processing ticket: {str(e)}")
                st.exception(e)

    st.divider()

    # Metrics and history
    tab1, tab2 = st.tabs(["📊 Metrics", "📜 History"])

    with tab1:
        render_metrics()

    with tab2:
        render_history()

    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with LangChain, LangGraph, Groq API & Streamlit | "
        "Multi-Agent System with Guardrails & Evaluation"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
