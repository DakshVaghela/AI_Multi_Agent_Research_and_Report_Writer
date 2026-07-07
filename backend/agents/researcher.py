from backend.models.citation import Citation
from backend.models.research_note import ResearchNote
from backend.search.search_service import search_service
from backend.services.content_extraction_service import (
    content_extraction_service,
)
from backend.services.summarization_service import (
    summarization_service,
)
from backend.state.agent_state import ResearchState


class ResearchAgent:
    """
    Research every question from the planner and
    store one structured research note per question.
    """

    def run(
        self,
        state: ResearchState,
    ) -> ResearchState:

        if not state.research_plan:
            return state

        # Process every research question
        for index, sub_question in enumerate(state.research_plan, start=1):

            print("\n" + "=" * 80)
            print(f"Research Question {index}")
            print("=" * 80)
            print(sub_question)

            results = search_service.search(
                query=sub_question,
                max_results=3,
            )

            if not results:
                print("No search results found.")
                continue

            # For now, use the best result only.
            combined_article = ""
            citations = []

            successful = False

            for result in results:

                print(f"Trying: {result.title}")

                article = content_extraction_service.extract(
                    str(result.url)
                )

                if not article:
                    print("Extraction failed.")
                    continue

                combined_article += f"""

            ==================================================
            Source: {result.title}
            ==================================================

            {article}

            """

                citation = Citation(
                    title=result.title,
                    url=result.url,
                    source=result.source,
                    snippet=result.content[:200],
                )

                citations.append(citation)

                successful = True

            if not successful:
                print("❌ Could not extract any article for this question.")
                continue

            print(f"✓ Successfully extracted {len(citations)} source(s)")

            summary = summarization_service.summarize(
                combined_article
            )

            note = ResearchNote(
                sub_question=sub_question,
                source_title=f"{len(citations)} Sources",
                source_url=str(citations[0].url),
                summary=summary.summary,
                key_points=summary.key_points,
                citations=citations,
            )

            state.research_notes.append(note)
            state.citations.extend(citations)

            print("✓ Combined research note created.")

        print("\n" + "=" * 80)
        print(f"Total Research Notes: {len(state.research_notes)}")
        print("=" * 80)

        return state