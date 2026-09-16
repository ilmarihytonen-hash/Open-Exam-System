# Server tools

Teacher exam APIs are exposed by the main FastAPI service:

- `GET /api/teacher/exams`
- `POST /api/teacher/exams`
- `POST /api/teacher/exams/{id}/status`
- `GET /api/teacher/exams/{id}/monitor`
- `POST /api/teacher/exams/{id}/delete`

SQLite data is stored in `data/oes.sqlite3` and remains until the owning teacher deletes an exam or an administrator deletes all exam data from the protected admin API.

## Debian 13 system controls

The administrator server API exposes read-only inventory at `/api/admin/server/overview` and validated actions for managed systemd services, hostname, timezone, reboot, and poweroff. It never accepts arbitrary shell commands. Mutating actions require:

1. `OES_ALLOW_SYSTEM_CHANGES=1` on the server.
2. A root-owned sudoers rule allowing only the required exact commands.
3. The administrator session and CSRF token.

Example sudoers policy, to be adapted for the service account:

```text
oesadmin ALL=(root) NOPASSWD: /usr/bin/systemctl status oes-server.service, /usr/bin/systemctl restart oes-server.service, /usr/bin/systemctl start oes-server.service, /usr/bin/systemctl stop oes-server.service, /usr/bin/hostnamectl set-hostname *, /usr/bin/timedatectl set-timezone *, /usr/bin/systemctl reboot, /usr/bin/systemctl poweroff
```

Do not grant `sudo ALL` to the web process.

## Local root shell

`root-shell.sh` is intentionally local-only and is not exposed by FastAPI. On Debian, install the files with an administrator account and run:

```bash
chmod +x server-tools/root-shell.sh
sudo ./server-tools/root-shell.sh
```

The script refuses to run unless it is already root. Do not create a web endpoint that launches it or accepts shell commands.
