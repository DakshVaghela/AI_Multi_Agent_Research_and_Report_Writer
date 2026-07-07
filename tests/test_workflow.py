from pathlib import Path

from backend.graph.workflow import research_workflow
from backend.services.report_service import report_service
from backend.state.agent_state import ResearchState


def test_workflow():

    state = ResearchState(
        topic="Impact of AI in Healthcare Diagnostics"
    )

    final_state = research_workflow.run(state)

    report = (
        final_state.final_report
        if final_state.final_report is not None
        else final_state.draft_report
    )

    assert report is not None

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "research_report.pdf"

    report_service.export_pdf(
        report=report,
        output_path=str(output_file),
    )

    print("\n")
    print("=" * 80)
    print("TITLE")
    print("=" * 80)
    print(report.title)

    print("\n")
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(report.executive_summary)

    print("\n")
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print(report.conclusion)

    print("\nPDF Generated:")
    print(output_file.resolve())