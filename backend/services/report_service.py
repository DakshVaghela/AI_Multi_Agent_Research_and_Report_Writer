from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from backend.models.report import Report


class ReportService:

    def export_pdf(
        self,
        report: Report,
        output_path: str,
    ) -> None:

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        doc = SimpleDocTemplate(output_path)

        styles = getSampleStyleSheet()

        story = [

            Paragraph(f"<b>{report.title}</b>", styles["Heading1"]),

            Paragraph("<b>Executive Summary</b>", styles["Heading2"]),
            Paragraph(report.executive_summary, styles["BodyText"]),

            Paragraph("<b>Introduction</b>", styles["Heading2"]),
            Paragraph(report.introduction, styles["BodyText"]),

            Paragraph("<b>Main Discussion</b>", styles["Heading2"]),
            Paragraph(report.main_content, styles["BodyText"]),

            Paragraph("<b>Conclusion</b>", styles["Heading2"]),
            Paragraph(report.conclusion, styles["BodyText"]),
        ]

        doc.build(story)


report_service = ReportService()