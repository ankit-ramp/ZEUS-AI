from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime

vendor_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert data extractor working for Zeus Packaging.
        Your task is to accurately extract  vendor name from data from PDF invoice documents.

        Current time: {time}

        **Instructions:**
        1. Cannot be Zeus packaging.
        2. do not send any hidden characters and trim any unecessary spaces. 

        """
    ),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system", "Ensure the final output is a valid JSON object that exactly matches the structure and types shown above."
    )
]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)

def get_vendor_prompt():
    return vendor_prompt_template
