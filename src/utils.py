def messages_to_prompt(messages):
    prompt = ""
    for message in messages:
        if message.role == "system":
            prompt += f"<|start_header_id|>system<|end_header_id|>{message.content}<|eot_id|>\n"
        elif message.role == "user":
            prompt += (
                f"<|start_header_id|>user<|end_header_id|>{message.content}<|eot_id|>\n"
            )
        elif message.role == "assistant":
            prompt += f"<|start_header_id|>assistant<|end_header_id|>{message.content}<|eot_id|>\n"

    # ensure we start with a system prompt, insert blank if needed
    if not prompt.startswith("<|start_header_id|>system<|end_header_id|>"):
        prompt = "<|start_header_id|>system<|end_header_id|><|eot_id|>\n" + prompt

    # add final assistant prompt
    prompt = prompt + "\n<|start_header_id|>assistant<|end_header_id|>"

    return prompt


def completion_to_prompt(completion):
    return f"<|start_header_id|>user<|end_header_id|>{completion}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
