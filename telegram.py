import telegram

def go_to_first_message(channel_id, date=None):
    if date is None:
        date = "01/01/2023"

    chat = telegram.Chat(channel_id)
    messages = chat.get_messages(
        limit=chat.total_messages,
        date=date,
    )

    if messages:
        first_message = messages[0]
        chat.scroll_to(first_message)

go_to_first_message("@Nature")
