This software is free to use and distribute under the GNU GPLv3 (GNU General Public License v3.0).

## Current release

Version `0.2.0-beta.1` (Beta), released 2026-09-16.

## Administrator server settings

Set these environment variables before starting FastAPI:

- `OES_ADMIN_PASSWORD`: administrator password, default `admin` for local development.
- `OES_ADMIN_USERNAME`: administrator username, default `admin`.
- `OES_TEACHER_PASSWORD`: teacher password, default `teacher` for local development.
- `OES_SESSION_KEY`: optional Fernet key; otherwise the server creates `.session.key` on first start.
- `OES_COOKIE_SECURE=1`: enable the Secure cookie flag when serving through HTTPS.

Administrator pages are served through protected `/admin/...` routes. Their session state is encrypted, expires after eight hours, and settings changes require CSRF validation.

The development defaults are `admin` and `teacher`. Change both before deployment.

Teacher pages are served through protected `/teacher/...` routes after login with the teacher credentials. If port 8000 is already in use, `run.py` automatically selects the next free port; use `--strict-port` to keep the old fail-fast behavior.

HTML files are never served directly. Administrator and teacher pages must be reached through their authenticated backend routes. Stop old/duplicate server processes before testing; run only `python run.py` from this project directory.

Install the backend dependencies with `python -m pip install -r requirements.txt`, then start the server with `python run.py --reload` for development. The same commands work on Linux and Windows 11; use `OES_HOST` and `OES_PORT` or `--host` and `--port` to change the bind address.

## Clustering

The administrator cluster page supports explicit private-network discovery, TCP health checks, weighted round-robin load distribution, and primary/replica or active/active modes. Discovery is limited to one CIDR with at most 254 hosts and never scans arbitrary networks. Nodes that fail health checks are excluded from traffic selection while healthy nodes remain available as replicas.

## Exams and student clients

Exam data is stored in `data/oes.sqlite3`. Student answers are upserted every second by the exam page, and violation events are retained with the exam. Teachers can delete only their own exams; administrators can delete all exam data through the protected admin API. The KDE client scripts are in `student-client/`.

Teachers can create individual accounts from the administrator user page. Passwords are stored as salted scrypt hashes, and each exam is owned by the teacher account that created it. The exam maker supports written, multiple-choice, ordering, and file-upload questions, character/file limits, image/audio media URLs, question points, named parts, and a persisted part-lock policy.

If a teacher cannot log in because an old password is persisted in `data/oes.sqlite3`, open Administrator -> Teacher accounts and use Reset password. The page shows usernames, display names, and enabled status, but never displays plaintext passwords.

Browser code cannot enforce a complete operating-system lockdown. The Linux monitor reports configured forbidden processes and tab-focus changes; use kiosk policy, a dedicated exam account, firewall rules, and managed KDE policies for stronger enforcement.

This software contains/will contain next features:
  status:    feature:
  not done    A vm(virtual machine) that has the examination enviorement inside of it and is simple and easy to install and use for the examinee and examiner.
  not done    A simple to Use and install Linux server software that can be easily installed.
  not done    Examinee software MAC support.
  not done    Examinee software Linux support.
  not done    Examinee software Windows Support.
  Not done    A web based control panel for the examiner to monitor and control(stop and pause) the exam.
  Not done    Detection for examinee malpractice or more simply said cheating.
  Not done    Examination builder and saving to the server's local drive.
  Not done    Secure and encrypted link betwean the server and client(Examinee / Examiner).

  Notes:
  This software is/will be highly optimized to run on any computer.
