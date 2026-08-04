import json


def classify_redeem_response(response):
    """Return a normalized result for Kingshot redeem responses."""
    if response is None:
        return {"valid": False, "reason": "empty", "message": ""}

    if isinstance(response, str):
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return {"valid": False, "reason": "invalid_json", "message": response}
    else:
        data = response

    msg = str(data.get("msg", "")).strip().lower()
    err_code = data.get("err_code")

    if data.get("success") is True:
        return {"valid": True, "reason": "success", "message": msg}

    if err_code == 40007 or "time error" in msg or "time expired" in msg:
        return {"valid": False, "reason": "code_expired", "message": msg}

    if err_code == 40014 or "cdk not found" in msg:
        return {"valid": False, "reason": "code_invalid", "message": msg}

    if err_code == 40020 or "user info error" in msg:
        return {"valid": False, "reason": "player_invalid", "message": msg}

    if any(text in msg for text in ["already received", "already redeemed", "cdk used", "limit"]):
        return {"valid": True, "reason": "already_redeemed", "message": msg}

    if any(text in msg for text in ["player not found", "role not exist", "fid error"]):
        return {"valid": False, "reason": "player_invalid", "message": msg}

    return {"valid": False, "reason": "unknown", "message": msg}


def validate_redeem_response(response):
    return classify_redeem_response(response)["valid"]