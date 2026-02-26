# Security Review

**Date:** 2026-02-26
**Branch:** main
**Reviewer:** Claude Code (automated security review)
**Scope:** Full codebase — `app.py`, `marketnews.py`, `db_setup.py`, Jinja2 templates

---

## Summary

No exploitable vulnerabilities were found. The codebase applies correct security controls for its threat model as a read-only news aggregation application.

---

## Controls Verified

### SQL Injection — PASS

All database queries use parameterized statements via `mysql.connector`. User-supplied input (search query, article ID, page number) is never concatenated into SQL strings.

```python
# app.py:48-51 — search query parameterized correctly
cursor.execute("""
    WHERE t.ticker LIKE %s
    ORDER BY m.created_at DESC
    LIMIT %s OFFSET %s
""", (f'%{search_query}%', limit, offset))
```

The `LIKE` wildcard wrapping (`%{search_query}%`) occurs in the Python parameter value, not in the SQL statement itself, and is handled safely by the database driver.

### Cross-Site Scripting (XSS) — PASS

Flask enables Jinja2 autoescaping by default for all `.html` templates. All variables rendered in `index.html` and `article.html` are autoescaped without use of the `|safe` filter or `Markup()` bypasses. Article URLs originate from the AlphaVantage API (a trusted upstream source) and are not user-supplied.

### Debug Mode — PASS

`app.run(debug=True)` at `app.py:181` is guarded by `if __name__ == '__main__':`. In production, the app is served by Gunicorn (`CMD ["uv", "run", "gunicorn", ...]` in the Dockerfile), which imports the module without executing that block. Debug mode is never active in the deployed container.

### Route Parameter Type Safety — PASS

The article detail route uses Flask's `<int:article_id>` type converter (`app.py:131`), which rejects non-integer values before they reach the database layer.

### Input Handling — PASS

The `page` and `q` query parameters are the only external inputs. Both are consumed in a read-only path with no write operations exposed via the web interface.

---

## Notes

- The `.env` file is used for local development only and should not be committed to version control. Confirm `.env` is listed in `.gitignore` and that production secrets are injected via the Docker Compose environment or a secrets manager.
- The `marketnews_pass` default database password in `app.py:32` is used as a fallback for local development. Ensure the production environment always overrides `DB_PASSWORD` via the environment.

---

## Verdict

**No action required.** The application correctly prevents SQL injection, XSS, and type confusion attacks within its current feature set.
