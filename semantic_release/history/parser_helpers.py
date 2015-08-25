
def parse_text_block(text):
    """
    This will take a text block and return a tuple with body and footer,
    where footer is defined as the last paragraph.

    :param text: The text string to be divided.
    :return: A tuple with body and footer,
    where footer is defined as the last paragraph.
    """
    body, footer = '', ''
    if text:
        body = text.split('\n\n')[0]
        if len(text.split('\n\n')) == 2:
            footer = text.split('\n\n')[1]

    return body.replace('\n', ' '), footer.replace('\n', ' ')
