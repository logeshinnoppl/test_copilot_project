# Requirement Brief — Contact Submission Form

> Reference ID: LOCAL-20261023-contact-form   Requested by: Logesh K   Date: 2026-10-23

1. **Business objective** — The site currently has no way for visitors to reach out. A contact form lets visitors submit inquiries that the site owner can review via a simple admin list, giving the site a basic inbound-contact channel.

2. **User story**
   - As a website visitor, I want to submit a contact message (name, email, subject, message), so that I can reach the site owner with an inquiry.
   - As the site owner, I want to view submitted contact messages, so that I can follow up on inquiries.

3. **Acceptance criteria**
   - AC1: Given the contact page is loaded, when I view the form, then I see required fields Name, Email, Subject, Message (each marked required) and a Submit button.
   - AC2: Given all fields are filled with valid values, when I click Submit, then the backend stores the submission in SQLite with a timestamp and I am redirected to a thank-you page confirming receipt.
   - AC3: Given any required field is empty, when I click Submit, then the form is not submitted, an inline validation error is shown per empty field, and no record is written to the database.
   - AC4: Given the Email field is not a valid email format, when I click Submit, then an inline validation error is shown for Email and no record is written.
   - AC5: Given at least one submission exists, when I navigate to the admin submissions page, then I see a list (name, email, subject, message, submitted timestamp) ordered newest first.
   - AC6: Given zero submissions exist, when I navigate to the admin page, then it shows an explicit empty-state message instead of an empty table.
   - AC7: Given I navigate to `/admin/submissions` without valid credentials, when prompted for Basic Auth, then access is denied (401) until correct credentials are supplied.

4. **UI reference (Figma/screenshot)** — N/A, no Figma/design provided. Plain HTML/CSS, styled simply and consistently with the existing `index.html`.

5. **Technical constraints**
   - Backend: Python 3, Flask.
   - Storage: SQLite, single local file-based DB.
   - Admin page (`/admin/submissions`) protected by HTTP Basic Auth; credentials read from `ADMIN_USERNAME` / `ADMIN_PASSWORD` environment variables — never hardcoded or committed. App fails fast at startup with a clear error if these env vars are unset.
   - No performance/load budget specified — assumed low-traffic, single instance.

6. **Components / modules affected** (suggested — confirm during planning)
   - `app.py` — Flask app entrypoint, basic-auth check, env var loading
   - `/` or `/contact` — contact form page
   - `/submit` (POST) — validation + DB insert
   - `/thank-you` — confirmation page
   - `/admin/submissions` (GET, Basic Auth protected) — list view
   - `db.py` / schema — SQLite `submissions` table (id, name, email, subject, message, created_at)
   - `requirements.txt`

7. **Edge cases & error handling**
   - Empty required field(s) → inline error, no DB write
   - Invalid email format → inline error, no DB write
   - Field length caps (name/email/subject ≤200 chars, message ≤2000 chars) → reject oversized input with validation error
   - Submitted content is escaped on render in the admin list (prevent stored XSS)
   - DB write failure → generic error shown to user, no internal error/stack trace exposed
   - Missing/incorrect Basic Auth credentials → 401
   - `ADMIN_USERNAME` / `ADMIN_PASSWORD` unset at startup → explicit startup error, not silent open access
   - No duplicate-submission detection, spam filtering, or CAPTCHA (explicitly out of scope)

8. **Testing scope**
   - Unit (pytest): validation logic, DB insert/fetch
   - Integration: `POST /submit` (valid → redirect + row created; invalid → errors + no row), `GET /admin/submissions` (401 without credentials, 200 with correct credentials)
   - E2E (Playwright): fill form → submit → verify thank-you redirect → verify submission appears on admin page (with credentials)

9. **Browser / device scope** — Latest Chrome, Firefox, Safari; desktop viewport only (no mobile/responsive requirement stated — assumption).

10. **Analytics / tracking** — None.

11. **Out of scope** — Email notifications, spam/CAPTCHA/rate-limiting, editing/deleting submissions, multi-user admin accounts/roles/password reset, visual design system, deployment/hosting config.

12. **Definition of done** — AC1–AC7 pass via automated tests (unit + integration + Playwright e2e) run locally with exit code 0; code-review returns no unresolved Critical/High findings; PR opened against `main`.

## Confirmation
Confirmed by: Logesh K on 2026-10-23   Waived items (if any): none
