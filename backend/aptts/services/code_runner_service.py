import io
import contextlib

def execute_user_code(code: str, input_data: str, return_dict):
    try:
        local_vars = {}
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(code, {}, local_vars)
            if 'solution' not in local_vars:
                raise Exception("Function 'solution' not defined")
            args = input_data.strip().split()
            args = [int(x) for x in args]
            result = local_vars['solution'](*args)
        return_dict['output'] = str(result).strip()
    except Exception as e:
        return_dict['error'] = str(e)