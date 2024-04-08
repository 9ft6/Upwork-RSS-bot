import json
import pickle

from pydantic import BaseModel

from config import cfg
from logger import logger


class Storage:
    items: dict

    def __init__(self, update_callback=None):
        self.items = {}
        self.update_callback = update_callback
        logger.info(f"Loading dataset... "
                    f"total: {len(self.items)} jobs in database")
        self.load()

    def __setitem__(self, key, value):
        result = self.items.__setitem__(key, value)
        self.dump()
        return result

    def __getitem__(self, item):
        return self.items.__getitem__(item)

    def __iter__(self):
        return iter(self.items)

    def count(self):
        return len(self.items)

    def show(self, _filter=None):
        for item in self.items.values():
            if not _filter or _filter(item):
                logger.info(item)

    def export(self):
        with open('export.json', 'w') as file:
            items = {i: s.dict() for i, s in self.items.items()}
            json.dump(items, file)

    def dump(self):
        try:
            with open(cfg.jobs_file, 'wb') as file:
                pickle.dump(self.items, file)
        except Exception as e:
            logger.error(f"Cannot dump pickle {e}")


    def load(self):
        try:
            with open(cfg.jobs_file, 'rb') as file:
                self.items = pickle.load(file)
        except Exception as e:
            logger.error(f"Cannot read pickle {e}")


class Jobs(Storage):
    def get_new(self, jobs: list):
        new_jobs = []
        for job in jobs:
            if job.id not in self.items:
                new_jobs.append(job)
                self.put(job)
        self.dump()
        return new_jobs

    def put(self, item: dict | list | BaseModel):
        match item:
            case dict():
                [self.put(j) for j in item.values()]
            case list():
                [self.put(j) for j in item]
            case BaseModel():
                self[item.id] = item
            case _:
                logger.error(f'Jobs: Unknown item type "{type(item)}"')


jobs = Jobs()
