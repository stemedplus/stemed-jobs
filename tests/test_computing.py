"""Computing is its own discipline in the shared STEMEd+ discipline list (ANZSRC 46), not Engineering."""
import unittest

from stemed_jobs.disciplines import classify_disciplines
from stemed_jobs.models import Job
from stemed_jobs.relevance import is_stem_education_relevant


def relevant(title, discipline, categories=("faculty",)):
    job = Job(
        id=title, title=title, company="", location="", url="https://jobs.example/x", published="",
        summary="", source="s", source_url="u", categories=list(categories), functions=[],
        disciplines=classify_disciplines(title, ""),
    )
    return is_stem_education_relevant(job, discipline)


class ComputingTests(unittest.TestCase):
    def test_computer_science_is_computing(self):
        self.assertEqual(classify_disciplines("Assistant Teaching Professor of Computer Science", ""), ["Computing"])
        self.assertEqual(classify_disciplines("Postdoc in Computer Science Education", ""), ["Computing"])

    def test_math_and_computer_science_is_both(self):
        self.assertEqual(
            classify_disciplines("Math and Computer Science Learning Specialist", ""), ["Computing", "Mathematics"]
        )

    def test_teaching_and_education_research_roles_are_listed(self):
        self.assertTrue(relevant("Assistant Teaching Professor of Computer Science", "Computing"))
        self.assertTrue(relevant("Postdoc in Computing Education Research", "Computing", ("postdocs",)))

    def test_computer_science_research_roles_are_not(self):
        self.assertFalse(relevant("Assistant Professor of Computer Science", "Computing"))
