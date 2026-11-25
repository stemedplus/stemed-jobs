import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from stemed_jobs.models import Job
from stemed_jobs.storage.rss_store import ALL_FEED, NO_POSTINGS_TITLE, render_rss, write_rss_feeds


def job(id, title, categories, disciplines):
    return Job(id=id, title=title, company="State U", location="Anywhere", url="https://jobs.example/" + id,
               published="2026-11-20T00:00:00Z", summary="A position in education research.", source="Test",
               source_url="https://feeds.example/test", categories=categories, functions=["research"],
               disciplines=disciplines, curated=True)


class AllJobsFeed(unittest.TestCase):
    def test_every_listed_job_once_with_its_disciplines(self):
        jobs = [job("a", "Chemistry education postdoc", ["postdocs"], ["Chemistry", "Science Education"]),
                job("b", "Physics teaching faculty", ["faculty"], ["Physics"]),
                job("c", "Not for any audience", [], ["Physics"])]
        root = ElementTree.fromstring(render_rss(jobs))
        items = root.findall("./channel/item")
        self.assertEqual([i.findtext("title") for i in items], ["Chemistry education postdoc", "Physics teaching faculty"])
        self.assertEqual([c.text for c in items[0].findall("category")][:2], ["Chemistry", "Science Education"])
        self.assertEqual(root.findtext("./channel/title"), "STEMEd+ Jobs: all jobs")

    def test_empty_feed_has_a_placeholder(self):
        root = ElementTree.fromstring(render_rss([]))
        self.assertEqual(root.findtext("./channel/item/title"), NO_POSTINGS_TITLE)

    def test_written_next_to_the_other_feeds(self):
        with tempfile.TemporaryDirectory() as d:
            count = write_rss_feeds([job("b", "Physics teaching faculty", ["faculty"], ["Physics"])], Path(d))
            self.assertTrue((Path(d) / ALL_FEED).exists())
        self.assertEqual(count, 85)


if __name__ == "__main__":
    unittest.main()
