import re

from backend.models.report import Report
from backend.prompts.writer import (
    MAIN_CONTENT_SECTIONS,
    WRITER_CONCLUSION_SYSTEM_PROMPT,
    WRITER_EXECUTIVE_SUMMARY_SYSTEM_PROMPT,
    WRITER_INTRODUCTION_SYSTEM_PROMPT,
    WRITER_SECTION_SYSTEM_PROMPT,
    WRITER_TITLE_SYSTEM_PROMPT,
)
from backend.services.llm_service import llm_service
from backend.state.agent_state import ResearchState


def _clean_plain_text(text: str) -> str:
    """
    Light cleanup of a plain-text (non-JSON) LLM response: strip
    surrounding whitespace, an accidental ```code fence``` wrapper, or a
    single pair of wrapping quotes around the whole response.
    """

    text = (text or "").strip()

    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        text = text[1:-1].strip()

    return text


_REFERENCES_HEADING_RE = re.compile(r"(?im)^\s*references\s*:?\s*$")


def _strip_fabricated_references(text: str) -> str:
    """
    The writer LLM sometimes appends its own "References" list with
    invented sources, despite being told not to -- the report's real
    reference list is compiled separately from the actual search
    results. Cut the text at the first such heading line.
    """

    match = _REFERENCES_HEADING_RE.search(text or "")

    if not match:
        return text or ""

    return text[: match.start()].rstrip()


def _strip_leading_heading(text: str, name: str) -> str:
    """
    Drop a leading line that just repeats the section's own name.
    Despite being told not to include a heading, the model sometimes
    writes the section name as its first line anyway, duplicating the
    "## {name}" heading the PDF already renders above it.
    """

    text = (text or "").strip()
    first_line, _, rest = text.partition("\n")

    if first_line.strip().strip("#").strip().rstrip(":").lower() == name.lower():
        return rest.lstrip()

    return text


def _dedupe_paragraphs(text: str) -> str:
    """
    Drop paragraphs that repeat an earlier paragraph in the same text.

    Small models asked for a strict minimum word count sometimes pad by
    repeating an earlier paragraph (near-)verbatim, especially closing
    "in conclusion..." style paragraphs. Comparing a normalized prefix of
    each paragraph catches exact and near-duplicate repeats.
    """

    seen = set()
    kept = []

    for block in re.split(r"\n\s*\n", (text or "").strip()):
        block = block.strip()

        if not block:
            continue

        signature = " ".join(block.lower().split())[:100]

        if signature in seen:
            continue

        seen.add(signature)
        kept.append(block)

    return "\n\n".join(kept)


# Raw scraped article text can run to tens of thousands of characters per
# note (up to 3 full sources per question). Dumped in uncapped across 5-6
# notes, it blows past the model's context window, Ollama silently
# truncates the prompt, and the writer LLM's output comes back broken.
# Capping keeps every note's source material a bounded, predictable size
# while still giving the writer far more grounding than the
# summary/key_points alone.
MAX_SOURCE_CHARS_PER_NOTE = 4000

# Ollama's grammar-constrained JSON decoding let the model "cheat" by
# emitting a trivially valid empty string instead of writing real
# content -- observed failing on real research notes roughly 3 times out
# of 4. Plain-text generation (no json_mode) fixes that failure mode, but
# still occasionally comes back blank; retrying beats silently shipping
# an empty section.
MAX_GENERATION_ATTEMPTS = 3


class WriterAgent:
    """
    Generates a research report from research notes.
    Can also improve an existing report using critic feedback.

    The report is assembled from several focused, plain-text LLM calls
    (title, executive summary, introduction, one per main-content
    section, conclusion) rather than one big JSON call:

    - A small local model reliably ignores per-section length
      instructions when it also has to juggle five other sections in
      the same response, but is much more likely to hit a target word
      count when writing one section at a time.
    - json_mode's grammar-constrained decoding let the model satisfy the
      schema with an empty string instead of actually writing the
      section; plain prose avoids that shortcut entirely.
    """

    def run(
        self,
        state: ResearchState,
        feedback: str = "",
    ) -> ResearchState:

        notes = self._build_notes_block(state.research_notes)
        condensed_notes = self._build_condensed_notes_block(state.research_notes)

        # Title/executive-summary/introduction only need the summary + key
        # points to do their job -- skipping the raw source dumps keeps
        # those calls from re-processing the same large prompt the section
        # calls need for grounding.
        title = self._generate_title(condensed_notes, feedback)
        executive_summary = self._generate_executive_summary(condensed_notes, feedback)
        introduction = self._generate_introduction(condensed_notes, feedback)

        sections = []

        for name, focus in MAIN_CONTENT_SECTIONS:
            content = self._generate_section(notes, name, focus, feedback)
            sections.append(f"## {name}\n\n{content}")

        main_content = "\n\n".join(sections)

        conclusion = self._generate_conclusion(condensed_notes, feedback)

        data = {
            "title": title,
            "executive_summary": executive_summary,
            "introduction": introduction,
            "main_content": main_content,
            "conclusion": conclusion,
        }

        for field in ("title", "executive_summary", "introduction", "conclusion"):
            data[field] = data[field] or (
                f"[The model did not return a '{field.replace('_', ' ')}' "
                "section for this draft.]"
            )

        report = Report(
            **data,
            references=state.citations,
        )

        state.draft_report = report

        return state

    def _generate_with_retry(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        num_predict: int,
        num_ctx: int,
        extract,
        label: str,
    ) -> str:
        """
        Call the LLM and clean/extract with `extract(response) -> str`,
        retrying the same prompt if the result comes back empty.
        """

        result = ""

        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            response = llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.4,
                num_predict=num_predict,
                num_ctx=num_ctx,
                json_mode=False,
            )

            result = extract(response)

            if result:
                return result

            print(
                f"⚠ Writer: '{label}' came back empty "
                f"(attempt {attempt}/{MAX_GENERATION_ATTEMPTS})."
            )

        print(f"⚠ Writer: '{label}' stayed empty after {MAX_GENERATION_ATTEMPTS} attempts.")

        return result

    def _build_notes_block(self, research_notes) -> str:
        notes = ""

        for index, note in enumerate(research_notes, start=1):

            key_points = "\n".join(
                f"- {point}" for point in note.key_points
            )

            source_content = note.full_content[:MAX_SOURCE_CHARS_PER_NOTE]

            notes += f"""
Research Note {index}

Question:
{note.sub_question}

Summary:
{note.summary}

Key Points:
{key_points}

Source Content:
{source_content}

------------------------------------------------------------

"""

        return notes

    def _build_condensed_notes_block(self, research_notes) -> str:
        """
        Same shape as `_build_notes_block` but without the raw scraped
        "Source Content" -- used for the title/executive-summary/
        introduction/conclusion calls, which only need the gist of each
        note, not the full article text the section-writing calls use for
        grounding.
        """

        notes = ""

        for index, note in enumerate(research_notes, start=1):

            key_points = "\n".join(
                f"- {point}" for point in note.key_points
            )

            notes += f"""
Research Note {index}

Question:
{note.sub_question}

Summary:
{note.summary}

Key Points:
{key_points}

------------------------------------------------------------

"""

        return notes

    def _feedback_block(self, notes: str, feedback: str, instructions: str) -> str:
        return f"""
Research Notes

{notes}

Reviewer Feedback

{feedback}

Instructions:

{instructions}
"""

    def _generate_title(self, notes: str, feedback: str) -> str:

        prompt = self._feedback_block(
            notes,
            feedback,
            "- If reviewer feedback is empty, write the first draft of the title.\n"
            "- Otherwise, revise it according to the reviewer feedback.",
        )

        return self._generate_with_retry(
            system_prompt=WRITER_TITLE_SYSTEM_PROMPT,
            user_prompt=prompt,
            num_predict=64,
            num_ctx=8192,
            extract=_clean_plain_text,
            label="title",
        )

    def _generate_executive_summary(self, notes: str, feedback: str) -> str:

        prompt = self._feedback_block(
            notes,
            feedback,
            "- If reviewer feedback is empty, write the first draft of the "
            "executive summary.\n"
            "- Otherwise, revise it according to the reviewer feedback.",
        )

        return self._generate_with_retry(
            system_prompt=WRITER_EXECUTIVE_SUMMARY_SYSTEM_PROMPT,
            user_prompt=prompt,
            num_predict=1024,
            num_ctx=16384,
            extract=lambda response: _dedupe_paragraphs(
                _strip_fabricated_references(_clean_plain_text(response))
            ),
            label="executive summary",
        )

    def _generate_introduction(self, notes: str, feedback: str) -> str:

        prompt = self._feedback_block(
            notes,
            feedback,
            "- If reviewer feedback is empty, write the first draft of the "
            "introduction.\n"
            "- Otherwise, revise it according to the reviewer feedback.",
        )

        return self._generate_with_retry(
            system_prompt=WRITER_INTRODUCTION_SYSTEM_PROMPT,
            user_prompt=prompt,
            num_predict=1024,
            num_ctx=16384,
            extract=lambda response: _dedupe_paragraphs(
                _strip_fabricated_references(_clean_plain_text(response))
            ),
            label="introduction",
        )

    def _generate_section(
        self,
        notes: str,
        name: str,
        focus: str,
        feedback: str,
    ) -> str:

        system_prompt = WRITER_SECTION_SYSTEM_PROMPT.format(
            section_name=name,
            section_focus=focus,
        )

        prompt = self._feedback_block(
            notes,
            feedback,
            "- If reviewer feedback is empty, write the first draft of this section.\n"
            "- Otherwise, revise this section according to the reviewer feedback.",
        )

        def extract(response):
            cleaned = _strip_fabricated_references(_clean_plain_text(response))
            cleaned = _strip_leading_heading(cleaned, name)
            return _dedupe_paragraphs(cleaned)

        return self._generate_with_retry(
            system_prompt=system_prompt,
            user_prompt=prompt,
            num_predict=2048,
            num_ctx=16384,
            extract=extract,
            label=name,
        )

    def _generate_conclusion(self, notes: str, feedback: str) -> str:

        prompt = self._feedback_block(
            notes,
            feedback,
            "- If reviewer feedback is empty, write the first draft of the conclusion.\n"
            "- Otherwise, revise it according to the reviewer feedback.",
        )

        return self._generate_with_retry(
            system_prompt=WRITER_CONCLUSION_SYSTEM_PROMPT,
            user_prompt=prompt,
            num_predict=1536,
            num_ctx=16384,
            extract=lambda response: _dedupe_paragraphs(
                _strip_fabricated_references(_clean_plain_text(response))
            ),
            label="conclusion",
        )
