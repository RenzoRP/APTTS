import sys
import io
import traceback

def execute_user_code(code, input_data, print_based, return_dict):
    try:
        local_vars = {}

        if print_based:
            # Capture print output
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()

            # Execute code (assumes function prints directly)
            exec(code, {}, local_vars)

            # If a function is defined, call it with inputs
            if 'main' in local_vars:
                local_vars['main'](*input_data)
            sys.stdout = old_stdout

            return_dict['output'] = redirected_output.getvalue().strip()
            return_dict['error'] = None

        else:
            # Normal return-based logic
            exec(code, {}, local_vars)
            if 'main' not in local_vars:
                raise Exception("Function 'main' not defined")

            result = local_vars['main'](*input_data)
            return_dict['output'] = str(result).strip()
            return_dict['error'] = None

    except Exception as e:
        if print_based:
            sys.stdout = old_stdout  # Reset stdout on error
        return_dict['output'] = None
        return_dict['error'] = traceback.format_exc()