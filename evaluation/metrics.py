"""Metrics Tracking Module"""
from typing import Dict, List, Any
from datetime import datetime
import json


class MetricsTracker:
    """Tracks various metrics for agent performance evaluation"""

    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.session_start = datetime.now()

    def log_interaction(
        self,
        ticket_id: str,
        category: str,
        confidence: float,
        response_time: float,
        escalated: bool,
        guardrail_violations: List[str],
        agent_used: str
    ):
        """
        Log a single interaction

        Args:
            ticket_id: Unique ticket identifier
            category: Ticket category
            confidence: Confidence score (0.0 to 1.0)
            response_time: Time taken to respond (seconds)
            escalated: Whether ticket was escalated
            guardrail_violations: List of guardrail violations
            agent_used: Which agent handled the ticket
        """
        interaction = {
            "ticket_id": ticket_id,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "confidence": confidence,
            "response_time": response_time,
            "escalated": escalated,
            "guardrail_violations": guardrail_violations,
            "agent_used": agent_used
        }
        self.metrics.append(interaction)

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics

        Returns:
            Dictionary of summary statistics
        """
        if not self.metrics:
            return {
                "total_interactions": 0,
                "avg_response_time": 0,
                "avg_confidence": 0,
                "escalation_rate": 0,
                "total_violations": 0
            }

        total = len(self.metrics)
        avg_response_time = sum(m['response_time'] for m in self.metrics) / total
        avg_confidence = sum(m['confidence'] for m in self.metrics) / total
        escalated = sum(1 for m in self.metrics if m['escalated'])
        escalation_rate = (escalated / total) * 100
        total_violations = sum(len(m['guardrail_violations']) for m in self.metrics)

        # Category breakdown
        category_counts = {}
        for m in self.metrics:
            cat = m['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Agent performance
        agent_performance = {}
        for m in self.metrics:
            agent = m['agent_used']
            if agent not in agent_performance:
                agent_performance[agent] = {
                    'count': 0,
                    'total_confidence': 0,
                    'total_response_time': 0
                }
            agent_performance[agent]['count'] += 1
            agent_performance[agent]['total_confidence'] += m['confidence']
            agent_performance[agent]['total_response_time'] += m['response_time']

        # Calculate averages for each agent
        for agent, stats in agent_performance.items():
            stats['avg_confidence'] = stats['total_confidence'] / stats['count']
            stats['avg_response_time'] = stats['total_response_time'] / stats['count']

        return {
            "total_interactions": total,
            "avg_response_time": round(avg_response_time, 2),
            "avg_confidence": round(avg_confidence, 3),
            "escalation_rate": round(escalation_rate, 2),
            "total_violations": total_violations,
            "category_breakdown": category_counts,
            "agent_performance": agent_performance
        }

    def export_metrics(self, filepath: str = "metrics_log.json"):
        """
        Export metrics to JSON file

        Args:
            filepath: Path to save metrics
        """
        data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "summary": self.get_summary_stats(),
            "interactions": self.metrics
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_recent_metrics(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get n most recent interactions

        Args:
            n: Number of recent interactions to return

        Returns:
            List of recent interactions
        """
        return self.metrics[-n:] if self.metrics else []
