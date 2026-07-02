import trafilatura


class ReaderTool:

    def extract(self, url: str):

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        content = trafilatura.extract(downloaded)

        return content or ""


reader_tool = ReaderTool()