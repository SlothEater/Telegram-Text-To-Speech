import openai

openai.api_key = ""

def generate_chat_response(query) -> str:
    """
    Generate a chatbot response based on the user's query.

    Parameters:
        query (str): The user's query.

    Returns:
        str: The generated chatbot response.
    """
    prompt = [
        {"role": "system", "content": "You are a chatbot"},
        {"role": "user", "content": query},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt
    )

    # TODO Add handling for no API tokens

    result = ""
    for choice in response.choices:
        result += choice.message.content

    return result

def set_openai_api_key(api_key):
    """
    Set the OpenAI API key.

    Parameters:
        api_key (str): The OpenAI API key.
    """
    openai.api_key = api_key
