from openai import OpenAI

class AI:
    def __init__(self, model, system_prompt, base_url, api_key):
        self.model = model
        self.system_prompt = system_prompt

        self.ai_client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def query_ai(self, user_prompt, temperature, max_tokens):
        completion = self.ai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ], max_tokens=max_tokens, temperature=temperature
        )

        return completion.choices[0].message.content