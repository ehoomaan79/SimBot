from database import add_code, remove_code



def extract_codes(message):

    """
    Extract gift codes from Kingshot messages.
    Modify this according to actual format.
    """

    codes=[]


    words = message.split()


    for word in words:

        word = word.strip(
            "`!.,\n"
        )


        # example code format
        if len(word) >= 5 and word.isalnum():

            codes.append(word)



    return codes



def process_message(message):

    codes = extract_codes(message)


    for code in codes:

        added = add_code(code)


        if added:

            print(
                "New code:",
                code
            )