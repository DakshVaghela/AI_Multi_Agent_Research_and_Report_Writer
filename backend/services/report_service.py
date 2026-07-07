import re
from datetime import datetime
from html import escape
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents

from backend.models.report import Report

# Paragraph styles that count as Table-of-Contents / outline entries,
# mapped to their TOC nesting level.
_TOC_STYLES = {
    "SectionHeading": 0,
    "SubHeading": 1,
}


class _ReportDocTemplate(BaseDocTemplate):
    """
    A DocTemplate that records the page number of every heading as the
    document is laid out, so the Table of Contents (built with
    multiBuild) can show real page numbers, and so headings become
    clickable entries in the PDF's outline/bookmark panel.
    """

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return

        level = _TOC_STYLES.get(flowable.style.name)
        if level is None:
            return

        text = flowable.getPlainText()
        key = f"toc-{id(flowable)}"

        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


class ReportService:
    """
    Renders a Report into a formatted, multi-page PDF:
    - A title page, followed by a real Table of Contents with page
      numbers (computed via a two-pass build).
    - Distinct heading styles for sections and main-content subsections.
    - Real paragraph breaks (main_content is split on blank lines).
    - "## Heading" markers inside main_content become styled subheadings.
    - Every top-level section (Introduction, Main Discussion, Conclusion,
      References) and every main-content subsection starts on its own page.
    - A numbered, hyperlinked reference list built from report.references.
    """

    def _build_styles(self):
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=styles["Title"],
                fontSize=24,
                leading=29,
                alignment=TA_CENTER,
                spaceAfter=18,
            )
        )
        styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=styles["Normal"],
                fontSize=12,
                leading=16,
                alignment=TA_CENTER,
                textColor="#555555",
            )
        )
        styles.add(
            ParagraphStyle(
                name="TOCTitle",
                parent=styles["Heading1"],
                fontSize=18,
                spaceAfter=16,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading1"],
                fontSize=15,
                spaceBefore=18,
                spaceAfter=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SubHeading",
                parent=styles["Heading2"],
                fontSize=12.5,
                spaceBefore=12,
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Body",
                parent=styles["BodyText"],
                fontSize=10.5,
                leading=15,
                alignment=TA_JUSTIFY,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Reference",
                parent=styles["BodyText"],
                fontSize=9.5,
                leading=13,
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="TOCLevel0",
                parent=styles["Normal"],
                fontSize=11.5,
                leading=18,
                leftIndent=0,
                fontName="Helvetica-Bold",
            )
        )
        styles.add(
            ParagraphStyle(
                name="TOCLevel1",
                parent=styles["Normal"],
                fontSize=10.5,
                leading=15,
                leftIndent=18,
            )
        )

        return styles

    def _paragraphs(self, text: str, style: ParagraphStyle) -> list:
        """Split text on blank lines and render each block as its own Paragraph."""

        flowables = []

        for block in re.split(r"\n\s*\n", (text or "").strip()):
            block = block.strip()
            if not block:
                continue
            block = escape(block).replace("\n", "<br/>")
            flowables.append(Paragraph(block, style))

        return flowables

    def _main_content_flowables(self, main_content: str, styles) -> list:
        main_content = (main_content or "").strip()

        if not main_content:
            return []

        parts = re.split(r"(?m)^##\s*(.+?)\s*$", main_content)

        if len(parts) == 1:
            # No "## Heading" markers -- render as plain paragraphs.
            return self._paragraphs(main_content, styles["Body"])

        flowables = []

        if parts[0].strip():
            flowables.extend(self._paragraphs(parts[0], styles["Body"]))

        is_first_subsection = not parts[0].strip()

        for i in range(1, len(parts), 2):
            heading = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""

            # Every subsection after the first starts on its own page --
            # the first one is skipped since it already opens on the fresh
            # page the "Main Discussion" heading started.
            if not is_first_subsection:
                flowables.append(PageBreak())
            is_first_subsection = False

            flowables.append(Paragraph(escape(heading), styles["SubHeading"]))
            flowables.extend(self._paragraphs(body, styles["Body"]))

        return flowables

    def _references_flowables(self, report: Report, styles) -> list:
        if not report.references:
            return []

        flowables = [
            PageBreak(),
            Paragraph("References", styles["SectionHeading"]),
        ]

        items = []
        for citation in report.references:
            label = escape(f"{citation.title} — {citation.source}")
            url = escape(str(citation.url))
            entry = f'{label}<br/><link href="{url}" color="blue">{url}</link>'
            items.append(
                ListItem(Paragraph(entry, styles["Reference"]), spaceAfter=8)
            )

        flowables.append(ListFlowable(items, bulletType="1", leftIndent=18))

        return flowables

    def _toc(self, styles) -> TableOfContents:
        toc = TableOfContents()
        toc.levelStyles = [styles["TOCLevel0"], styles["TOCLevel1"]]
        toc.dotsMinLevel = 0
        return toc

    def export_pdf(
        self,
        report: Report,
        output_path: str,
    ) -> None:

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        styles = self._build_styles()

        doc = _ReportDocTemplate(
            str(output_path),
            pagesize=LETTER,
            topMargin=0.9 * inch,
            bottomMargin=0.9 * inch,
            leftMargin=0.9 * inch,
            rightMargin=0.9 * inch,
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id="normal",
        )
        doc.addPageTemplates([PageTemplate(id="report", frames=[frame])])

        story = [
            Spacer(1, 1.8 * inch),
            Paragraph(escape(report.title), styles["ReportTitle"]),
            Paragraph(
                f"Research Report — Generated {datetime.now():%B %d, %Y}",
                styles["ReportSubtitle"],
            ),
            PageBreak(),
            Paragraph("Table of Contents", styles["TOCTitle"]),
            self._toc(styles),
            PageBreak(),
            Paragraph("Executive Summary", styles["SectionHeading"]),
            *self._paragraphs(report.executive_summary, styles["Body"]),
            PageBreak(),
            Paragraph("Introduction", styles["SectionHeading"]),
            *self._paragraphs(report.introduction, styles["Body"]),
            PageBreak(),
            Paragraph("Main Discussion", styles["SectionHeading"]),
            *self._main_content_flowables(report.main_content, styles),
            PageBreak(),
            Paragraph("Conclusion", styles["SectionHeading"]),
            *self._paragraphs(report.conclusion, styles["Body"]),
        ]

        story.extend(self._references_flowables(report, styles))

        doc.multiBuild(story)


report_service = ReportService()
