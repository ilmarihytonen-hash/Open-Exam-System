# KDE Plasma student client

These scripts target Linux with KDE Plasma and Firefox.

- `start_exam.sh`: sets Firefox as the HTTP/HTTPS handler when possible and opens the exam in kiosk mode.
- `monitor_allowed_apps.sh`: checks for configured forbidden process names every second and reports violations to the server when a session cookie is supplied. It does not kill processes.
- `remote_poweroff.sh`: sends a non-interactive `sudo systemctl poweroff` over SSH after confirmation. Configure passwordless sudo for that command; do not put passwords in the script.

Example:

```bash
export OES_EXAM_URL=http://server:8000/student/login
./start_exam.sh
```
