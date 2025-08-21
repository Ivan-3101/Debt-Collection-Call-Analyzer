from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools

def calculate_call_quality_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates key call quality metrics from conversation data.
    
    This function processes a list of utterances to compute total duration, speaking times,
    overtalk, and silence periods. It handles empty input data gracefully.
    """
    if not data:
        return {
            "total_duration": 0, "overtalk_percentage": 0, "silence_percentage": 0,
            "speaking_time": 0, "agent_speaking_time": 0, "customer_speaking_time": 0,
            "speaking_intervals": []
        }

    # Calculate speaking intervals and individual talk times in one pass
    speaking_intervals = []
    agent_time = 0
    customer_time = 0
    for entry in data:
        start, end = entry.get('stime', 0), entry.get('etime', 0)
        speaker = entry.get('speaker', '').lower()
        speaking_intervals.append({'start': start, 'end': end, 'speaker': speaker})
        
        duration = end - start
        if speaker == 'agent':
            agent_time += duration
        else:
            customer_time += duration
    
    total_speaking_time = agent_time + customer_time
    total_duration = max(entry['end'] for entry in speaking_intervals) if speaking_intervals else 0

    # Calculate overtalk duration more concisely using itertools
    overtalk_duration = 0
    for interval1, interval2 in itertools.combinations(speaking_intervals, 2):
        if interval1['speaker'] != interval2['speaker']:
            overlap_start = max(interval1['start'], interval2['start'])
            overlap_end = min(interval1['end'], interval2['end'])
            if overlap_start < overlap_end:
                overtalk_duration += (overlap_end - overlap_start)

    silence_duration = total_duration - total_speaking_time + overtalk_duration

    return {
        "total_duration": total_duration,
        "speaking_time": total_speaking_time,
        "agent_speaking_time": agent_time,
        "customer_speaking_time": customer_time,
        "overtalk_duration": overtalk_duration,
        "silence_duration": max(0, silence_duration),
        "overtalk_percentage": round((overtalk_duration / total_duration * 100) if total_duration > 0 else 0, 2),
        "silence_percentage": round((silence_duration / total_duration * 100) if total_duration > 0 else 0, 2),
        "speaking_intervals": speaking_intervals
    }

def create_call_quality_visualizations(metrics: Dict[str, Any]) -> go.Figure:
    """Creates a 2x2 dashboard of call quality visualizations."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Call Composition', 'Speaking Timeline', 'Quality Metrics', 'Speaker Distribution'),
        specs=[[{"type": "pie"}, {"type": "scatter"}], [{"type": "bar"}, {"type": "pie"}]]
    )
    
    speaker_colors = {'agent': '#2E8B57', 'customer': '#4169E1'}

    # 1. Call Composition Pie Chart
    comp_labels = ['Speaking Time', 'Silence', 'Overtalk']
    comp_values = [
        metrics.get('speaking_time', 0) - metrics.get('overtalk_duration', 0),
        metrics.get('silence_duration', 0),
        metrics.get('overtalk_duration', 0)
    ]
    fig.add_trace(go.Pie(labels=comp_labels, values=comp_values, marker_colors=['#2E8B57', '#FFB6C1', '#FF6B6B']), row=1, col=1)

    # 2. Speaking Timeline
    for interval in metrics.get('speaking_intervals', []):
        speaker = 'agent' if 'agent' in interval.get('speaker', '') else 'customer'
        fig.add_trace(go.Scatter(
            x=[interval['start'], interval['end']], y=[speaker, speaker],
            mode='lines', line=dict(color=speaker_colors[speaker], width=10), showlegend=False
        ), row=1, col=2)
    # Timeline Legend
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name='Agent', marker=dict(color=speaker_colors['agent'], size=10)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name='Customer', marker=dict(color=speaker_colors['customer'], size=10)), row=1, col=2)
    
    # 3. Quality Metrics Bar Chart
    fig.add_trace(go.Bar(
        x=['Overtalk %', 'Silence %'], 
        y=[metrics.get('overtalk_percentage', 0), metrics.get('silence_percentage', 0)],
        marker_color=['#FF6B6B', '#FFB6C1']
    ), row=2, col=1)
    
    # 4. Speaker Distribution Pie Chart (uses pre-calculated values)
    dist_labels = ['Agent', 'Customer']
    dist_values = [metrics.get('agent_speaking_time', 0), metrics.get('customer_speaking_time', 0)]
    fig.add_trace(go.Pie(labels=dist_labels, values=dist_values, marker_colors=[speaker_colors['agent'], speaker_colors['customer']]), row=2, col=2)
    
    fig.update_layout(height=800, title_text="Call Quality Dashboard", showlegend=True)
    fig.update_xaxes(title_text="Time (s)", row=1, col=2)
    fig.update_yaxes(categoryorder='array', categoryarray=['customer', 'agent'], row=1, col=2) # Ensures 'Agent' is on top
    fig.update_yaxes(title_text="Percentage (%)", row=2, col=1)
    
    return fig