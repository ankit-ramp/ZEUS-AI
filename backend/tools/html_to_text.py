from bs4 import BeautifulSoup

def extract_text_from_html(path):
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, "html.parser")

                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text(separator="\n", strip=True)
                return text
            except Exception as e:
                print(f"Error extracting text from HTML file {path}: {e}")
                return ""