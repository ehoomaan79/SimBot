from giftcodes import process_message



KINGSHOT_CHANNEL_ID = 1260478586188730398



async def handle_message(message):


    if message.channel.id != KINGSHOT_CHANNEL_ID:
        return


    print(
        "Kingshot:",
        message.content
    )


    process_message(
        message.content
    )