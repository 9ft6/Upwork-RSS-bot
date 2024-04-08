from openai import OpenAI

from config import cfg

translate_prompt = "translate into {language}: {text}"
annotate_prompt = (
    "In one sentence in {language}, the essence of the order, "
    "without listing skills and extra words. Maximum 30 words."
    "{text}"
)


class Translator(OpenAI):
    def __init__(self):
        super().__init__(api_key=cfg.openai_key)

    def translate(self, text: str):
        prompt = translate_prompt.format(
            language=cfg.target_language,
            text=text,
        )
        return self.send(prompt)

    def annotate(self, job: str):
        prompt = annotate_prompt.format(
            language=cfg.target_language,
            text=job.description,
        )
        return self.send(prompt)

    def send(self, content: str):
        response = self.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            n=1,
            stop=None,
            messages=[
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content


translator = Translator()
