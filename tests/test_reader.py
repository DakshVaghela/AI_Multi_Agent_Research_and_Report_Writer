from backend.tools.reader_tool import reader_tool

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

content = reader_tool.extract(url)

print(content[:2000])