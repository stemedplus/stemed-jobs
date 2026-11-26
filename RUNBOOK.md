# Runbook: Jobs

This board uses the shared STEMEd+ pipeline. For how every board works and the common fixes, see the [stemedplus-theme runbook](https://github.com/stemedplus/stemedplus-theme/blob/main/RUNBOOK.md).

| | |
|---|---|
| **Site** | stemedplus.github.io/stemed-jobs |
| **Repository** | stemedplus/stemed-jobs |
| **Updates** | Daily at 06:00 UTC, on push, and by hand (workflow: `regenerate-feeds.yml`) |
| **Sources** | 56 RSS feeds in `config/feeds.json` (Chronicle, jobRxiv, AAPT, AGU, Science Careers, and others); 30 linked job boards in `config/job_boards.json` |
| **Submitted jobs** | `submitted/`, added automatically from the **Post a job** issue form (`add-position.yml`) |
| **Build** | `python -m stemed_jobs` |
| **Protected** | `main` needs a pull request with passing tests (`tests.yml`) |

**Add a job board or feed:** add it to `config/feeds.json` (pulled) or `config/job_boards.json` (linked only), and record it in the Source and Permissions Log.

**A posted job is wrong or spam:** close its issue and delete its file in `submitted/` through a pull request.

**A job is in the wrong list:** people report it with the **Wrong list** form. Adjust the matching rules or the job's file.

_Written November 2026. Review with the yearly December review._
