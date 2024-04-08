from datetime import datetime
from hashlib import md5

from pydantic import Field, BaseModel

from gpt import translator
from logger import logger


class Job(BaseModel):
    title: str
    link: str
    description: str
    content: str | None = Field(None, alias='content:encoded')
    time: str
    id: str | None = None

    money: str | None
    category: str | None
    country: str | None
    skills: list[str] | None

    class Config:
        populate_by_name = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.link:
            self.id = md5(self.link.encode()).hexdigest()

    def __str__(self):
        return f'{self.time} {self.title[:70]:<70} {self.id}'

    @classmethod
    def from_soup(cls, item):
        try:
            return cls(
                title=item.find('title').text.replace("- Upwork", ""),
                link=item.find('link').text,
                description=cls.parse_description(item),
                money=cls.parse_money(item),
                country=cls.parse_country(item),
                skills=cls.parse_skills(item),
                time=cls.parse_date(item),
                category=cls.parse_category(item),
            )
        except Exception as e:
            logger.error(f"Cannot parse Job: {e}")

    @classmethod
    def get_tail(cls, item: str):
        description = item.find('content:encoded').get_text()
        return description.split("<br /><br /><b>")[1]

    @classmethod
    def parse_date(cls, item: str):
        return datetime.strptime(
            item.find('pubDate').text,
            "%a, %d %b %Y %H:%M:%S %z"
        ).ctime()[4:-5]

    @classmethod
    def parse_money(cls, item: str):
        tail = cls.get_tail(item)
        if tail.startswith('Budget') or tail.startswith('Hourly Range'):
            money = tail.split('\n')[0]
            return f"<b>{money}"

    @classmethod
    def parse_category(cls, item: str):
        tail = cls.get_tail(item)
        state = "<b>Category</b>: "
        if state in tail:
            category = tail.split(state)[1].split("<br />")[0]
            return category

    @classmethod
    def parse_country(cls, item: str):
        tail = cls.get_tail(item)
        state = "<b>Country</b>: "
        if state in tail:
            country = tail.split(state)[1].split("\n")[0]
            return country

    @classmethod
    def parse_skills(cls, item: str):
        tail = cls.get_tail(item)
        state = "<b>Skills</b>: "
        if state in tail:
            skills = tail.split(state)[1].split("<br />")[0]
            skills = list(map(lambda x: x.strip(), skills.split(",")))
            return skills

    @classmethod
    def parse_description(cls, item: str):
        description = item.find('content:encoded').get_text()
        for f, t in [
            ("<br /><br />", "<br />"),
            ("<br />", "\n"),
            ("&middot;", " 👉 "),
            ("&bull;", " 👉 "),
            ("&nbsp;", " "),
        ]:
            description = description.replace(f, t)
        description = description.split("<b>")[0]
        return description

    def get_message(self):
        skills = "\n         👉 ".join([f"{s}" for s in self.skills])
        money = f"<b>💵  {self.money}</b>" if self.money else ""
        header = (
            f'\n\n<b>{self.title}</b>\n\n'
            f"<b>❗️  {self.category}</b>\n"
            f"<b>📅  {self.time}    <b>🌎  {self.country}</b></b>\n"
            f"{money}\n"
            f"<b>🙈  Skills</b>:<code> 👉 {skills}\n\n</code>"
            f'<a href="{self.link}"><b>⚡️Apply⚡️</b></a>'
        )

        # TODO: keep translations in model and translate once - on demand
        annotation = translator.annotate(self)
        return annotation + header
