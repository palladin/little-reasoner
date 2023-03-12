import gradio as gr
import openai
import z3 
import re

openai.api_key = "YOUR OPENAI KEY"


def extract_code(code):
    pattern = r"```*.\n(.*?)\n```"
    match = re.search(pattern, code, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

def askGpt(messages): 
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    return completion.choices[0].message.content

def solve(script):
    try:
        solver = z3.Solver()
        solver.from_string(script)
        if solver.check() == z3.sat:
            model = solver.model()
            return model
        else:
            return "unsat"
    except:
        return None

def solve_worflow(question):
    messages = []
    messages.append({"role": "user", "content": question})
    messages.append({"role": "user", "content": "extract variables and assertions"})
    vars_assertions = askGpt(messages)
    print(vars_assertions)

    messages.append({"role": "assistant", "content": vars_assertions})
    messages.append({"role": "user", "content": "generate smt-lib vars and assertions"})
    reply = askGpt(messages)
    print(reply)
    messages.append({"role": "assistant", "content": reply})

    script = extract_code(reply)
    print(script)
    if script is None:
        return ("oups, something went wrong!", "oups, something went wrong!")
    result = solve(script)
    if result is None:
        return ("oups, something went wrong!", "oups, something went wrong!")
    
    messages = []
    messages.append({"role": "user", "content": question})
    messages.append({"role": "user", "content": f"ouput {result}, generate the final answer"})
    reply = askGpt(messages)
    print(reply)
    
    return (reply, script)

example = """
assert that 
c = 6557
a * b = c 
a, b > 1
try to find values for a and b 
"""

with gr.Blocks() as demo:
    question = gr.Textbox(label="Question", lines=5, value=example)
    smt = gr.Textbox(label="SMT", lines=5)
    solution = gr.Textbox(label="Solution", lines=5)
    solve_btn = gr.Button("Solve")
    solve_btn.click(fn=solve_worflow, inputs=question, outputs=[solution, smt])
    
demo.launch()