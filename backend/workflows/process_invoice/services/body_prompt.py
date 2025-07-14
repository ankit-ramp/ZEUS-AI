from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime



def get_body_prompt(body: str):

    body_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert data extractor working for Zeus Packaging.
        Your task is to accurately extract structured product/body data from PDF invoice documents.

        Current time: {time}

        **Instructions:**

        Extract an array of `invoice_lines`, each with the following fields:
        {body}
              
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system", "Ensure the final output is a valid JSON object that exactly matches the structure and types shown above."
    )
    ]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
    body = body
    )

    return body_prompt_template