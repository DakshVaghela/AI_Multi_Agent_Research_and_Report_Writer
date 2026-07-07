from concurrent.futures import ThreadPoolExecutor

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

            combined_article = ""
            citations = []

            # Sources are independent network fetches -- extracting them
            # concurrently instead of one-by-one collapses this from
            # N sequential round-trips to the slowest single one.
            with ThreadPoolExecutor(max_workers=len(results)) as executor:
                articles = list(
                    executor.map(
                        lambda r: content_extraction_service.extract(str(r.url)),
                        results,
                    )
                )

            for result, article in zip(results, articles):

                if not article:
                    print(f"Extraction failed: {result.title}")
                    continue

                print(f"✓ Extracted: {result.title}")

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

            successful = bool(citations)

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
                full_content=combined_article,
                citations=citations,
            )
            
            state.research_notes.append(note)
            state.citations.extend(citations)

            print("✓ Combined research note created.")

        print("\n" + "=" * 80)
        print(f"Total Research Notes: {len(state.research_notes)}")
        print("=" * 80)

        return state