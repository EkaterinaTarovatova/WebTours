def check_http_response(response, param_to_check):
    try:
        assert param_to_check in response.text
    except AssertionError:
        response.failure(f"Assertion Error: text pattern '{param_to_check}' was not found in response")
        return False
    else:
        # Если ассерт прошел успешно, значит, текст найден
        return True