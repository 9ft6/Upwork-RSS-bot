from bs4 import BeautifulSoup as bs

from .base import BaseWebClient
from config import cfg
from models import Job


class UpworkRSSClient(BaseWebClient):
    async def get_feed(self, session):
        self.session = session
        url = "https://www.upwork.com/ab/feed/jobs/rss"
        params = {
            "paging": "10",
            "sort": "recency",
            "api_params": "1",
            "q": cfg.upwork_query,
            "securityToken": cfg.upwork_token,
            "userUid": cfg.upwork_user_id,
            "orgUid": cfg.upwork_org_id,
        }
        response, status = await self.make_request(url, params=params)

        if status == 200:
            return self.parse_feed(response)

    def parse_feed(self, body: str):
        items = []
        for item in bs(body, features="xml").find_all("item"):
            if item := Job.from_soup(item):
                items.append(item)
        return items


__all__ = ['UpworkRSSClient']
