# AI Customer Support Orchestrator      
     
A sophisticated multi-agent system for automating customer support using AI agents with built-in guardrails, evaluation metrics, and real-time orchestration.
 
<img width="1103" height="611" alt="image" src="https://github.com/user-attachments/assets/008bbf79-da13-4c5c-b1c2-53b1599cf05c" />


[![Built with LangChain](https://img.shields.io/badge/Built%20with-LangChain-blue)](https://langchain.com/)
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io/)

##  Features

### Multi-Agent Architecture
- **Classifier Agent**: Intelligently categorizes support tickets into Technical, Billing, or General
- **Technical Support Agent**: Handles technical issues with web search capabilities
- **Billing Support Agent**: Manages billing, payment, and subscription queries
- **General Support Agent**: Answers general inquiries and information requests

### Advanced Guardrails
- **Content Filtering**: Prevents prohibited topics (medical, legal, financial advice)
- **Response Validation**: Ensures quality, completeness, and appropriate length
- **Escalation Rules**: Automatic detection of cases requiring human intervention
- **Safety Checks**: Comprehensive validation at each workflow step

### Evaluation & Metrics
- **Real-time Metrics**: Track response time, confidence scores, and escalation rates
- **Performance Analytics**: Category breakdown and agent performance comparison
- **Interaction Logging**: Complete audit trail of all interactions
- **Export Capabilities**: Download metrics for further analysis

### LangGraph Workflow
- Orchestrated multi-step workflow using LangGraph
- State management across agents
- Conditional routing based on ticket category
- Error handling and recovery

##  Architecture

```
┌─────────────┐
│   Ticket    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Classifier  │ ──► Category: Technical/Billing/General
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Router    │
└──────┬──────┘
       │
       ├─► Technical Agent (with Web Search)
       │
       ├─► Billing Agent
       │
       └─► General Agent (with Web Search)
       │
       ▼
┌─────────────┐
│  Guardrails │ ──► Content Filter, Validator
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Escalation  │ ──► Check if human needed
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))
- Serper API key ([Get one here](https://serper.dev))

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd customer-support-orchestrator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
TEMPERATURE=0.3
MAX_TOKENS=2048
```

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Orchestrator Programmatically

```python
from orchestrator import SupportOrchestrator

# Initialize orchestrator
orchestrator = SupportOrchestrator()

# Process a ticket
result = orchestrator.process_ticket(
    "My app crashes when I upload files"
)

# View response
print(f"Category: {result['category']}")
print(f"Response: {result['response']}")
print(f"Confidence: {result['confidence']}")
print(f"Escalated: {result['escalated']}")

# Get metrics
metrics = orchestrator.get_metrics()
print(metrics)

# Export metrics
orchestrator.export_metrics("metrics.json")
```
<img width="1861" height="830" alt="image" src="https://github.com/user-attachments/assets/622bbba7-782c-4bc2-af24-f0e7d6330494" />


<img width="1875" height="815" alt="image" src="https://github.com/user-attachments/assets/f765bb0d-2421-46ff-b6d9-78c9dfcbcd02" />


<img width="1071" height="816" alt="image" src="https://github.com/user-attachments/assets/4c8f133e-dce2-4d5b-b032-f987701bee69" />


##  Use Cases

### Customer Support Automation
- Automatically categorize and respond to support tickets
- Reduce response time and workload on human agents
- Ensure consistent quality in responses

### Intelligent Routing
- Route tickets to specialized agents based on content
- Escalate complex cases to human agents
- Handle multiple ticket types simultaneously

### Quality Assurance
- Monitor response quality with built-in metrics
- Track escalation rates and patterns
- Identify areas for improvement

##  Guardrails Configuration

Edit `config.yaml` to customize guardrails:

```yaml
guardrails:
  max_response_length: 1000
  min_response_length: 50
  prohibited_topics:
    - "medical advice"
    - "legal advice"
    - "financial investment advice"

  escalation_triggers:
    - "angry"
    - "lawsuit"
    - "lawyer"
    - "refund over 1000"

  confidence_threshold: 0.7
```

##  Metrics & Evaluation

The system tracks:
- **Response Time**: Time taken to process each ticket
- **Confidence Score**: AI's confidence in its response (0.0 - 1.0)
- **Escalation Rate**: Percentage of tickets escalated to humans
- **Category Accuracy**: Distribution of ticket categories
- **Agent Performance**: Per-agent metrics and statistics
- **Guardrail Violations**: Tracking of safety rule triggers

## Customization

### Adding New Agents

1. Create a new agent file in `agents/`:
```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def process(self, input_data):
        # Your logic here
        pass
```

2. Update the orchestrator workflow in `orchestrator/workflow.py`

### Modifying Guardrails

Edit the guardrail classes in `guardrails/`:
- `content_filter.py`: Content filtering rules
- `response_validator.py`: Response quality checks
- `escalation_rules.py`: Escalation logic

### Custom Evaluation Metrics

Extend `evaluation/metrics.py` to add new metrics:
```python
def track_custom_metric(self, value):
    # Your metric logic
    pass
```

## Project Structure

```
customer-support-orchestrator/
├── agents/               # AI agent implementations
│   ├── base_agent.py
│   ├── classifier_agent.py
│   ├── technical_agent.py
│   ├── billing_agent.py
│   └── general_agent.py
├── guardrails/          # Safety and validation
│   ├── content_filter.py
│   ├── response_validator.py
│   └── escalation_rules.py
├── evaluation/          # Metrics and evaluation
│   ├── metrics.py
│   └── evaluator.py
├── orchestrator/        # LangGraph workflow
│   └── workflow.py
├── utils/              # Utility functions
│   ├── llm_config.py
│   └── serper_search.py
├── app.py              # Streamlit UI
├── config.yaml         # Configuration
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  License

This project is licensed under the MIT License.

##  Acknowledgments

- **LangChain** for the agent framework
- **LangGraph** for workflow orchestration
- **Groq** for ultra-fast LLM inference
- **Serper** for web search capabilities
- **Streamlit** for the beautiful UI

##  Contact

For questions or feedback, please open an issue on GitHub.

---

