import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Iterable, List
from xml.etree import ElementTree

from stemed_jobs.disciplines import DISCIPLINES
from stemed_jobs.models import Job
from stemed_jobs.relevance import is_stem_education_relevant


NO_POSTINGS_TITLE = "No current postings"
CHANNEL_LINK = "https://stemedplus.github.io/stemed-jobs/"

AUDIENCES = ("graduates", "postdocs", "faculty", "staff", "teaching")
AUDIENCE_LABELS = {"staff": "Professional Staff", "teaching": "Teaching-Focused"}


def audience_label(audience: str) -> str:
    """How an audience is named to readers: "Professional Staff", "Faculty"..."""
    return AUDIENCE_LABELS.get(audience, audience.title())


def _slug(value: str) -> str:
    """"History & Philosophy of Science" -> "history-and-philosophy-of-science";
    "STEAM: Arts+STEM" -> "steam-arts-stem" (letters and digits only, as on the STEMEd+ Digest)."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", " and ")).strip("-")


ALL_FEED = "all.xml"


def feed_relative_path(audience: str, discipline: str) -> str:
    return "{}/{}.xml".format(_slug(audience), _slug(discipline))


def _listed(job: Job) -> List[str]:
    """The disciplines a job is listed under in at least one audience feed (empty: in no feed)."""
    if not any(audience in job.categories for audience in AUDIENCES):
        return []
    return [d for d in DISCIPLINES if d in job.disciplines and is_stem_education_relevant(job, d)]


def render_rss(jobs: Iterable[Job], audience: str = None, discipline: str = None) -> bytes:
    """One audience and discipline; with neither, every listed job once (feeds/all.xml)."""
    every = audience is None and discipline is None
    root = ElementTree.Element("rss", {"version": "2.0"})
    channel = ElementTree.SubElement(root, "channel")
    if every:
        ElementTree.SubElement(channel, "title").text = "STEMEd+ Jobs: all jobs"
        ElementTree.SubElement(channel, "description").text = (
            "Every job on STEMEd+ Jobs, for every audience and discipline. "
            "Listings are screened for STEM education research, STEM teaching, human dimensions, or cognitive science."
        )
    else:
        title = "{} jobs — {}".format(discipline, audience_label(audience))
        ElementTree.SubElement(channel, "title").text = "STEMEd+ Jobs: " + title
        ElementTree.SubElement(channel, "description").text = (
            "{} opportunities in {} across STEM education research and teaching. "
            "Listings are screened for STEM education research, STEM teaching, human dimensions, or cognitive science.".format(
                audience_label(audience), discipline
            )
        )
    ElementTree.SubElement(channel, "link").text = CHANNEL_LINK
    ElementTree.SubElement(channel, "language").text = "en"

    listed = 0
    for job in jobs:
        if every:
            disciplines = _listed(job)
            if not disciplines:
                continue
        else:
            if audience not in job.categories:
                continue
            if (
                discipline not in job.disciplines
                or not is_stem_education_relevant(job, discipline)
            ):
                continue
            disciplines = [discipline]
        listed += 1
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = job.title
        ElementTree.SubElement(item, "link").text = job.url
        ElementTree.SubElement(item, "guid", {"isPermaLink": "false"}).text = job.id
        if job.summary:
            ElementTree.SubElement(item, "description").text = job.summary
        if job.published:
            try:
                date = datetime.fromisoformat(job.published.replace("Z", "+00:00"))
                ElementTree.SubElement(item, "pubDate").text = format_datetime(date)
            except ValueError:
                pass
        for listed_discipline in disciplines:
            ElementTree.SubElement(item, "category").text = listed_discipline
        for function in job.functions:
            ElementTree.SubElement(item, "category").text = function.title()
        ElementTree.SubElement(item, "source", {"url": job.source_url}).text = job.source

    if not listed:
        # A feed with no items makes many readers and WordPress RSS widgets show
        # "an error has occurred... the feed is down". One placeholder item says
        # plainly that the feed works and has nothing to list right now.
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = NO_POSTINGS_TITLE
        ElementTree.SubElement(item, "link").text = CHANNEL_LINK
        if every:
            ElementTree.SubElement(item, "guid", {"isPermaLink": "false"}).text = "no-current-postings-all"
            ElementTree.SubElement(item, "description").text = (
                "There are no current postings right now. This list updates daily; check back soon."
            )
        else:
            ElementTree.SubElement(item, "guid", {"isPermaLink": "false"}).text = "no-current-postings-{}-{}".format(
                _slug(audience), _slug(discipline)
            )
            ElementTree.SubElement(item, "description").text = (
                "There are no current {} postings in {} right now. This list updates daily; check back soon.".format(
                    audience_label(audience).lower(), discipline
                )
            )
        ElementTree.SubElement(item, "pubDate").text = format_datetime(datetime.now(timezone.utc))

    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def write_rss_feeds(jobs: Iterable[Job], directory: Path) -> int:
    jobs = list(jobs)
    written = 0
    for audience in AUDIENCES:
        for discipline in DISCIPLINES:
            path = directory / feed_relative_path(audience, discipline)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(render_rss(jobs, audience, discipline))
            written += 1
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ALL_FEED).write_bytes(render_rss(jobs))
    return written  # the audience/discipline feeds; all.xml is written as well
