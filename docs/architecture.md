# Architecture

Rekordbox Library Intelligence follows a non-destructive data flow.

```text
Rekordbox
   |
   | Export XML
   v
XML Parser
   |
   v
Library Data
   |
   +--> Audit
   +--> Analytics
   +--> Classification (planned)
   |
   v
Reports / M3U8
```

## Principles
- Non-destructive by default
- Human in the loop
- Reproducible rules
- Privacy-first sample data
