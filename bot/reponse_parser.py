import json

def validate_redeem_response(response):

    try:
        data = json.loads(response)

    except json.JSONDecodeError:
        return False


    print(data)


    msg = str(
        data.get("msg", "")
    ).lower()


    # successful redemption
    if data.get("success") is True:
        return True


    # player exists but code already used
    valid_messages = [
        "already received",
        "already redeemed",
        "cdk used",
        "limit"
    ]


    for text in valid_messages:

        if text in msg:
            return True


    # invalid player
    invalid_messages = [
        "player not found",
        "role not exist",
        "fid error"
    ]


    for text in invalid_messages:

        if text in msg:
            return False


    return False