import hashlib
import logging
import os
from datetime import datetime
from random import randint
from typing import Optional

import shortuuid
from chalice import Chalice, Response
from pybadges import badge
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from pynamodb.models import Model
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = Chalice(app_name='views')
VIEW_TABLE_NAME = os.environ.get('VIEW_TABLE_NAME', 'ViewsCountTable_dev')


class ViewTable(Model):
    class Meta:
        table_name = VIEW_TABLE_NAME
        region = 'us-east-1'

    page_id = UnicodeAttribute(hash_key=True)
    service = UnicodeAttribute()
    total_views = NumberAttribute(default=0)
    last_updated = UTCDateTimeAttribute(default=datetime.utcnow())

    @classmethod
    def make_page_id(cls, service, url):
        return shortuuid.uuid(name=f"{service}_{url}")

    @classmethod
    def get_or_create(cls, page_id, **kwargs):
        try:
            page = cls.get(page_id)
        except cls.DoesNotExist:
            page = cls(page_id, **kwargs)
            page.save()
        return page

    @classmethod
    def patch_total_views(cls, page) -> int:
        page.update(actions=[
            cls.total_views.set(cls.total_views + 1),
            cls.last_updated.set(datetime.utcnow())
        ])
        return page.total_views


class GithubViewTable(ViewTable):
    class Meta:
        table_name = VIEW_TABLE_NAME
        region = 'us-east-1'

    user = UnicodeAttribute()
    repo = UnicodeAttribute()

    @classmethod
    def get_page(cls, user, repo):
        page_id = GithubViewTable.make_page_id('github', f"{user}_{repo}")
        return cls.get_or_create(page_id, service="github", user=user, repo=repo)


def make_badge(views: int):
    return badge(left_text='views', right_text=f"{views}", left_color='gray', right_color='green')


@app.route('/', methods=['GET'], cors=True)
def index():
    svg = badge(left_text='views', right_text=f"{randint(1, 100)}", left_color='gray', right_color='green')
    return Response(
        body=svg,
        status_code=200,
        headers={'Content-Type': 'image/svg+xml'})


def get_repo(repo: str) -> Optional[str]:
    data = repo.split('.')
    ext = data[-1]
    if ext == 'svg':
        return '.'.join(data[:-1])
    return


def make_etag(content:str):
    return hashlib.md5(f"{content}".encode('utf-8')).hexdigest


@app.route('/views/github/{user}/{repo}', methods=['GET'], cors=True)
def get_github_svg(user: str, repo: str):
    if repo := get_repo(repo):
        page = GithubViewTable.get_page(user, repo)
        total_views = GithubViewTable.patch_total_views(page)
        logger.info(
            "view history",
            extra={
                "service": "github",
                "user": user, "repo": repo,
                "total_views": total_views,
                "view_at": datetime.utcnow()
            }
        )
        badge = make_badge(total_views)
        # e_tag = make_etag(badge)
        return Response(
            body=badge,
            status_code=200,
            headers={
                'Content-Type': 'image/svg+xml',
                "Cache-Control": 'no-store',
                # "ETag": e_tag
            })
    else:
        return Response(
            body="you must have .svg extension",
            status_code=404,
            headers={'Content-Type': 'text/plain'}
        )
