from js2py import eval_js as js_eval


def eval_js(function: str) -> int | None:
    if function == 'document.querySelectorAll(\'body\').length':
        return 1

    elif function == 'window.location.host == \'clicker.joincommunity.xyz\' ? 129 : 578':
        return 129

    try:
        return int(js_eval(function))
    except Exception:
        return None
