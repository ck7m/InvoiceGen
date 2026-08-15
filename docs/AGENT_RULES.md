# Sai Krishna Networks GST Invoice Generator — AI Agent Rules

## 1. Purpose

These are mandatory rules for all AI coding agents working on the Sai Krishna Networks GST Invoice Generator.

The agent must read and follow:

1. `AGENT_RULES.md` — how the agent must work
2. `SAI_KRISHNA_NETWORKS_ARCHITECTURE.md` — system architecture
3. `SAI_KRISHNA_NETWORKS_DETAILED_SPEC.md` — functional and implementation requirements

The specification files are authoritative.

Do not silently change requirements.

---

# 2. Core Agent Behavior

## Rule 2.1 — Read before coding

Before making any code change:

1. Read `AGENT_RULES.md`.
2. Read the relevant sections of the architecture.
3. Read the relevant sections of the detailed specification.
4. Inspect the existing implementation.
5. Understand the existing project structure.
6. Then make the smallest appropriate change.

Do not start coding based only on the user's latest message if the change is related to an existing requirement.

## Rule 2.2 — Do not build ahead of the requested task

The project specification is divided into tasks.

Only implement the current requested task.

Do not automatically implement future functionality.

For example, if Task 1 is requested, do NOT automatically implement:

- Customer management
- Product management
- Invoice history
- Backup/restore
- Advanced settings
- E-invoicing
- E-way bill
- Cloud synchronization

unless specifically requested.

## Rule 2.3 — Complete the current task before moving forward

A task is not complete merely because the code has been written.

Before declaring completion:

- Run tests.
- Run the application where applicable.
- Test the relevant functionality.
- Inspect generated PDFs when applicable.
- Verify packaging when applicable.
- Fix failures.

Never claim something was tested if it was not actually tested.

---

# 3. Architecture Rules

## Rule 3.1 — Follow the architecture

The architecture described in `SAI_KRISHNA_NETWORKS_ARCHITECTURE.md` must be followed unless the user explicitly approves a change.

Do not introduce a different architecture simply because another pattern is fashionable.

## Rule 3.2 — Keep layers separate

Maintain separation between:

- UI
- Domain models
- Application/services
- GST calculation
- Persistence
- Invoice/document rendering
- PDF generation
- Printing/desktop integration

Do not put everything into one large Flet page/file.

## Rule 3.3 — UI must not contain business calculations

The Flet UI should collect and display information.

It must not become the authoritative location for:

- GST calculation
- invoice totals
- rounding
- tax calculation
- invoice numbering rules

The UI calls the appropriate domain/service layer.

## Rule 3.4 — PDF must not recalculate financial values

The PDF renderer must receive already calculated invoice data.

It must not independently calculate:

- GST
- totals
- tax
- rate including tax

There must be one authoritative calculation path.

## Rule 3.5 — Avoid unnecessary abstraction

Do not create excessive:

- interfaces
- factories
- base classes
- dependency injection frameworks
- repositories for every trivial object
- service layers that only forward a method call

Use abstractions when they provide a real architectural benefit.

Prefer simple, readable code.

---

# 4. Financial Accuracy Rules

These are the highest-priority rules in the project.

## Rule 4.1 — NEVER use float for money

Never use Python `float` for:

- Rate
- Quantity when fractional financial calculation is involved
- Tax percentage
- Tax amount
- Invoice amount
- GST
- Discount
- Totals

Use:

```python
from decimal import Decimal
```

## Rule 4.2 — Never construct Decimal from float

Forbidden:

```python
Decimal(0.1)
Decimal(1000.10)
```

Use:

```python
Decimal("0.1")
Decimal("1000.10")
```

instead.

## Rule 4.3 — All financial calculations use Decimal

Financial calculations must remain in Decimal form from input parsing through calculation and rounding.

Do not convert to float for convenience.

Do not convert to float before displaying a value.

## Rule 4.4 — Explicit rounding

The application must use an explicitly defined rounding policy.

Do not rely on implicit Python rounding behavior.

The currently specified default is:

```text
ROUND_HALF_UP
```

If the specification changes the rounding rule, update the GST engine and tests consistently.

## Rule 4.5 — No duplicate GST logic

There must be one authoritative GST calculation engine.

Do not implement one calculation in:

- Flet UI
- PDF renderer
- database layer
- invoice preview
- reports

and another calculation elsewhere.

## Rule 4.6 — Calculation changes require tests

Any modification to financial calculation code must include or update unit tests.

A financial calculation change is not complete until tests pass.

---

# 5. GST Calculation Rules

For an invoice item:

```text
Taxable Amount = Quantity × Rate

CGST Amount = Taxable Amount × CGST %

SGST Amount = Taxable Amount × SGST %

Total Tax = CGST Amount + SGST Amount

Amount With Tax = Taxable Amount + Total Tax
```

The application should also calculate:

```text
Rate With Tax =
    Rate
    + Rate × CGST %
    + Rate × SGST %
```

All calculations must use Decimal.

All rounding must follow the defined rounding policy.

---

# 6. Rounding and Persistence Rules

## Rule 6.1 — Define where rounding happens

Do not casually add rounding in multiple layers.

The GST engine must define exactly where values are rounded.

Document the decision in code comments/docstrings where it is not obvious.

## Rule 6.2 — Store historical calculation results

For finalized invoices, calculated values should be persisted.

This helps ensure that an old invoice remains reproducible if calculation code changes later.

Do not regenerate historical financial values using a future calculation implementation without an explicit migration/business rule.

---

# 7. PDF and Invoice Layout Rules

## Rule 7.1 — PDF is a document, not a screenshot

Never generate the invoice by taking a screenshot of the Flet UI.

The invoice must have its own document representation.

Preferred architecture:

```text
Invoice Data
    ↓
HTML/CSS Template
    ↓
PDF Renderer
    ↓
PDF
```

## Rule 7.2 — A4 is the target

Invoice PDFs must use A4 dimensions.

Do not allow content to accidentally resize the page horizontally.

## Rule 7.3 — Long descriptions are a first-class requirement

Descriptions can be:

- very short
- one line
- several lines
- very long

The invoice must handle all of them.

Long descriptions must:

- wrap
- increase row height
- preserve column alignment
- not overlap adjacent columns
- not overlap other rows
- not clip text

## Rule 7.4 — Never solve long text by shrinking everything

Do not make the entire invoice font tiny simply to accommodate a long description.

Prefer:

1. wrapping
2. dynamic row height
3. page continuation

## Rule 7.5 — Fixed numeric columns

Columns such as:

- Quantity
- Rate
- GST
- Amount
- HSN/SAC
- Batch

should have controlled widths.

The description column should receive the flexible space.

## Rule 7.6 — Page breaks

When the invoice spans multiple pages:

- Repeat table headers.
- Keep rows intact where practical.
- Do not overlap rows across pages.
- Put totals after the final item.
- Move declaration/bank/signatory sections to the next page if necessary.
- Never squeeze content into an unreadable layout simply to force one page.

## Rule 7.7 — Inspect PDFs

Successful PDF generation does NOT mean the PDF is correct.

When changing the invoice renderer, inspect actual generated PDFs.

Look for:

- clipping
- overlap
- incorrect wrapping
- incorrect page breaks
- broken totals
- broken headers
- incorrect alignment
- unreadable text

---

# 8. UI Rules

## Rule 8.1 — UI should remain simple

This is a small business application.

Do not introduce unnecessary:

- dashboards
- animations
- complex navigation
- visual effects
- excessive configuration

Prioritize usability.

## Rule 8.2 — Calculated fields should be visually distinguishable

The user-entered fields and calculated fields should be clear.

For example, the user enters:

```text
Quantity
Rate
CGST %
SGST %
```

The application calculates:

```text
Taxable Amount
CGST Amount
SGST Amount
Rate With Tax
Amount With Tax
```

## Rule 8.3 — Dynamic item rows

The invoice item table must support:

- Add item
- Remove item
- Editing existing items

The design should work for a small number of items without becoming cumbersome.

---

# 9. Database Rules

## Rule 9.1 — SQLite only unless explicitly changed

The initial application is local-first.

Do not introduce a server database.

## Rule 9.2 — Keep database access isolated

UI code should not contain raw SQL throughout the application.

Database operations should be isolated in the persistence/data-access layer.

## Rule 9.3 — Do not store derived values unnecessarily everywhere

Store authoritative invoice results where required for historical reproducibility.

Do not create redundant copies of every value without a reason.

## Rule 9.4 — Database schema changes

When changing the schema:

- Consider existing data.
- Do not casually delete or recreate the database.
- Use a migration/versioning strategy appropriate to the project's size.
- Preserve existing invoices.

---

# 10. Offline Rules

The application must work without internet access.

Do not introduce dependencies on:

- online GST services
- cloud databases
- web APIs
- online PDF generators
- cloud authentication
- remote configuration

unless explicitly requested.

---

# 11. Dependency Rules

Before adding a dependency:

1. Check whether Python/Flet already provides the functionality.
2. Check whether an existing dependency can provide it.
3. Consider maintenance and packaging implications.
4. Prefer mature, well-maintained libraries.
5. Avoid adding dependencies for trivial functionality.

Do not add a large framework to solve a small problem.

---

# 12. Error Handling Rules

Business users should see useful messages.

Bad:

```text
decimal.InvalidOperation
```

Good:

```text
Please enter a valid rate.
```

Technical details may be logged locally.

Do not expose stack traces to normal users.

---

# 13. Logging Rules

Use standard Python logging.

Logs should help diagnose:

- application errors
- PDF generation failures
- database errors
- unexpected exceptions

Do not unnecessarily log:

- customer PII
- complete invoice contents
- passwords
- secrets

---

# 14. Testing Rules

## Rule 14.1 — Tests are mandatory for financial logic

The GST engine must have automated tests.

At minimum test:

- 0%
- 5%
- 9%
- 12%
- 18%
- 28%
- decimal rates
- multiple quantities
- rounding boundaries
- small amounts
- large amounts
- multiple invoice items

## Rule 14.2 — Test invariants

Where applicable verify:

```text
total_tax = total_cgst + total_sgst

grand_total = taxable_total + total_tax
```

according to the defined rounding model.

## Rule 14.3 — Test edge cases

Do not test only the happy path.

Include:

- empty input
- zero
- invalid numbers
- very long descriptions
- many rows
- page boundaries
- unusual decimal values

## Rule 14.4 — Do not weaken tests to make code pass

If a test fails:

1. Understand why.
2. Determine whether the code or test is wrong.
3. Fix the correct thing.

Do not simply loosen the assertion.

---

# 15. Prototype Rules

The first development milestone is:

**Project Setup + Invoice Prototype**

The prototype must prove the technically risky parts before the rest of the application is built.

The prototype must include:

- Flet application
- invoice entry
- dynamic rows
- Decimal GST calculations
- long descriptions
- invoice preview
- HTML/CSS document
- PDF generation
- A4 layout
- automated GST tests
- Windows packaging

Do not build the complete product before the prototype is validated.

---

# 16. Scope Control

The agent must not expand scope without approval.

Examples of scope creep:

- Adding login
- Adding cloud synchronization
- Adding multi-user architecture
- Adding inventory
- Adding accounting
- Adding GST portal integration
- Adding e-invoice integration
- Adding e-way bill integration
- Adding mobile support during the prototype
- Adding reporting unrelated to the current task

If a feature is not required for the current task, leave it for the appropriate future task.

---

# 17. Handling Ambiguity

When requirements are unclear:

### If it affects financial correctness

STOP and ask the user.

Examples:

- GST rounding interpretation
- Tax calculation boundary
- Tax-inclusive pricing rules
- Invoice numbering rules that have legal implications
- Tax treatment that cannot safely be inferred

### If it is a minor implementation detail

Make a reasonable choice.

Document the choice.

Do not unnecessarily block development.

---

# 18. Handling Specification Conflicts

If the architecture and detailed specification appear to conflict:

1. Identify the conflict.
2. Do not silently choose one.
3. Determine whether it affects implementation or correctness.
4. If material, ask the user.
5. If it is only terminology or a minor implementation detail, choose the simpler consistent approach and document it.

Never silently rewrite the specification.

---

# 19. Code Change Discipline

Make small, understandable changes.

Avoid:

- rewriting unrelated files
- changing working code unnecessarily
- large refactors during feature implementation
- changing frameworks without approval
- renaming large portions of the project without reason

If a refactor is required, explain why.

---

# 20. Backward Compatibility

Once invoices are stored, assume they are important historical records.

Do not make changes that can silently invalidate existing invoices.

Before changing:

- database schema
- invoice model
- calculation behavior
- invoice serialization

consider existing data.

---

# 21. Security and Privacy

The application is local.

Do not:

- send invoice data to external services
- add telemetry without approval
- upload customer information
- expose a local server unnecessarily
- store credentials in source code

If a future external integration is required, explicitly identify the data being transmitted.

---

# 22. Packaging Rules

The final application should behave like a normal desktop application.

Windows:

```text
Desktop icon
    ↓
Double click
    ↓
Sai Krishna Networks Invoice Generator
```

The end user should not need to install Python.

The application should be packaged using the project's selected packaging approach.

Before declaring packaging complete:

- Build it.
- Install/run the built application.
- Verify it launches.
- Verify database access works.
- Verify PDF generation works.

---

# 23. Cross-platform Rules

Windows is the primary target.

macOS is secondary.

Do not sacrifice Windows usability for theoretical cross-platform purity.

However:

- avoid Windows-only APIs unless required
- isolate OS-specific functionality
- keep core business logic platform independent
- keep PDF generation platform independent

If a feature is Windows-only, isolate it behind a small platform-specific module.

---

# 24. AI Agent Communication Rules

At the beginning of a task, briefly state:

- what you understand the task to be
- which specification sections apply
- your implementation approach

During implementation:

- make the changes
- run relevant tests

At completion, report:

```text
Task:
Status:

Files changed:

Implementation:

Tests:
- test name
- result

Manual verification:

Known limitations:

Next recommended task:
```

Do not provide long explanations unless requested.

---

# 25. Never Claim Untested Results

Never say:

```text
The PDF prints correctly.
```

unless printing was actually tested.

Never say:

```text
The Windows executable works.
```

unless the built executable was actually launched/tested.

Never say:

```text
All tests pass.
```

unless the tests were actually run.

Use precise language such as:

```text
Unit tests passed locally.
Windows packaging was created but not executed in this environment.
```

when appropriate.

---

# 26. Do Not Hide Failures

If something cannot be completed:

1. State the failure.
2. Explain the likely cause.
3. State what was attempted.
4. State what remains.
5. Do not mark the task complete.

---

# 27. Definition of Task Completion

A task is complete only when:

- implementation matches the specification
- relevant tests pass
- relevant manual verification is performed
- no known critical defect remains
- changes are documented

For prototype work, PDF and UI behavior must be visually inspected.

---

# 28. Final Principle

Prioritize, in this order:

1. Financial correctness
2. Invoice correctness
3. Data integrity
4. Reliability
5. Simple maintainable architecture
6. Usability
7. Cross-platform support
8. Visual polish

Do not sacrifice financial correctness or invoice integrity for convenience or visual appearance.
