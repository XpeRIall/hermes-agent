# Source Manifest Patch

Apply these changes to `04_manifest/source_manifest.md`.

## 1. Actual repository inventory correction

The uploaded archive contains:

```text
02_repos/OpenHands-main.zip
02_repos/aider-main.zip
02_repos/claude-code-main.zip
02_repos/codex-main.zip
02_repos/crush-main.zip
02_repos/hermes-agent-main.zip
02_repos/langgraph-main.zip
02_repos/open-swe-main.zip
02_repos/plandex-main.zip
```

The original manifest's “Expected Systems vs Actual Pack Contents” section incorrectly states that fresh Hermes source is not included. Replace that row with:

| System | Included? | Evidence level available from this pack | Notes |
|---|---:|---|---|
| Hermes Fork / Hermes source | Yes | Source snapshot + thesis docs + prior reports | Use source code for implementation evidence. Treat thesis docs as design intent and prior reports as secondary analysis |

## 2. Missing systems

LangGraph is included.

Open SWE is included, but it is not SWE-agent proper.

SWE-agent proper is still not included. Either add actual SWE-agent source, instruct Deep Research to fetch official source/docs, or explicitly exclude SWE-agent from the comparison.

## 3. Crush/OpenCode identity

Keep the warning:

> The pack contains `crush-main.zip`; do not silently equate it with OpenCode unless research verifies the relationship.

## 4. Commit SHA gap

Add:

```text
04_manifest/repo_commit_shas.md
```

*ONLY* if exact upstream commits matter. Archive hashes alone are enough for this local research run but not for upstream provenance.

## 5. Naming cleanup

The file has already been renamed to:
```
01_project_thesis/founding_doubts.md
```
Update stale references from finding_doubts.md to founding_doubts.md *ONLY* if not renamed before

## 6. Add final output decision options

The final research must choose one:

- build full substrate runtime;
- build minimal governed promotion layer;
- build ledger/claims only;
- adopt existing framework and add governance;
- defer thesis;
- abandon thesis for now.
