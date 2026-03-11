## Feature 010: Contextual UI Panes and Left-Hand Navigation

**Overview:** Introduce a consistent shell layout with a left-hand navigation pane and reusable right-hand contextual panes so operators can access additional functionality (workflows, operations, POAMs, and vulnerability data) without cluttering the main content area.

This feature focuses on:

- A **left-hand navigation pane** that is present across authenticated pages.
- A **central content pane** where primary workflows, endpoint detail, and POAM pages render.
- A **right-hand contextual pane** pattern, starting with Vulnerability Management, that can be toggled open/closed.
- A new **Plan of Actions and Milestones (POAM)** navigation entry that leads to POAM management pages built around the existing `create-poam-entry` operation.

Work from this spec in order (one feature per branch); use backend contracts in `backend/existing-state/contracts/` as the source of truth for invocation and payloads.

---

## 1. Scope and boundaries

- **In scope**
  - Introduce a **global shell layout** with:
    - A persistent left-hand navigation pane.
    - A central main-content area reused by all key screens.
    - A right-hand contextual pane region that can host feature-specific panels.
  - Refactor:
    - Landing page (Workflows dashboard).
    - Endpoints index, Enclave detail, Endpoint detail.
  - Make the **Vulnerability Management** UI a reusable right-hand pane that appears on:
    - Enclave detail page.
    - Endpoint detail page.
  - Add navigation and UX scaffolding for **Plan of Actions and Milestones (POAM)** management, using:
    - `create-poam-entry` operation contract as the authoritative backend interface.
  - Define how **operations** and **workflows** are accessed via the left-hand navigation.
- **Out of scope**
  - Implementing backend storage or APIs beyond the existing `create-poam-entry` contract.
  - Adding new backend contracts for listing POAM entries; the front-end should be ready to call such a query if added later but should be able to work with stub/sample data in the meantime.
  - Changing the semantics of the vulnerability data source (covered by Feature 009).

---

## 2. Global shell layout

### 2.1 Base template refactor

- **File:** `landing/templates/landing/base.html`.
- **Goal:** Turn the base template into a shell with **three conceptual regions**:
  - Left: Navigation pane.
  - Center: Page-specific content.
  - Right: Optional contextual pane(s).

#### Requirements

- Keep the `<body class="app-shell">` and existing `<head>` contents (Bootstrap, theme CSS).
- Preserve existing template blocks:
  - `{% block title %}` for the document title.
  - `{% block content %}` for the main page body.
  - `{% block extra_js %}` for page-specific scripts.
- Preserve and reuse the existing **header content** (logo/title, prototype badge, user session actions), but relocate it inside the **main shell’s right-hand column** above the page content.
- Introduce a structural wrapper, e.g.:
  - `<div class="app-shell-layout">`
    - `<aside class="app-shell-sidebar">` (left nav).
    - `<div class="app-shell-main">`
      - (existing header)
      - `<main id="main-content">` with `{% block content %}`.
    - `</div>`
  - `</div>`
- Ensure that **unlock-user modal** and related JS remain functional and are still defined at the bottom of `base.html`.

### 2.2 Layout behavior and CSS hooks

- **File:** `landing/static/landing/css/theme.css`.
- Add shell-specific classes:
  - `.app-shell-layout` – flex container for sidebar + main regions.
  - `.app-shell-sidebar` – column for left nav.
  - `.app-shell-main` – column containing header and `<main>`.
  - `.app-shell-main-inner` (optional) – constrain header + content width using a container-like layout.
- **Desktop / large screens (≥ lg)**
  - Sidebar:
    - Fixed width (e.g. 260–280px).
    - Full height, scrolling independently if nav is tall.
  - Main content:
    - Occupies remaining horizontal space.
    - Vertical scrolling affects only this region; the sidebar remains visible.
- **Mobile / small screens**
  - Sidebar collapses into a toggleable element:
    - Option A (initial implementation): place the sidebar above main content and allow it to collapse using a simple **“Nav”** button in the header.
    - Sidebar may become an off-canvas element later; initial implementation can keep stacking simple and accessible.
  - Ensure that tab order and focus behavior remain intuitive when the sidebar is collapsed or expanded.

---

## 3. Left-hand navigation contents

The left-hand nav should clearly surface:

- **Workflows** (pipelines).
- **Endpoint Management** (endpoints index).
- **Plan of Actions and Milestones** (POAM management).
- **Operations** (Lambda operations), with a distinction between common and less common operations.

### 3.1 Workflows

- **Top-level item:** `Workflows`.
  - Clicking the top-level `Workflows` label navigates to the existing landing dashboard (`landing:home`).
- Beneath it, list each **major pipeline workflow** as child links:
  - Provision AD Connector / set up new enclave.
  - Provision Linux WorkSpace.
  - Provision Windows WorkSpace.
  - Provision EC2 instance.
- Each workflow link should:
  - Route to the existing **start pipeline execution** page for that pipeline ID.
  - Open the pipeline form in the central content pane, leaving left nav unchanged.

### 3.2 Endpoint Management

- **Top-level item:** `Endpoint Management`.
  - Route to the existing endpoints index view (`endpoints:index`, “Endpoints by enclave”).
  - When this item is active, highlight it in the sidebar.

### 3.3 Plan of Actions and Milestones (POAM)

- **Top-level item:** `Plan of Actions and Milestones`.
  - Route to a new POAM list view (e.g. `poam:list`) that:
    - Shows POAM entries grouped or filterable by **status** (`open`, `closed`).
    - Includes controls to switch between “Open POAMs” and “Closed POAMs” or to display all with a filter.
  - Provide a prominent **“Add POAM entry”** action on this page that navigates to a create/edit screen (or opens an in-page form).

#### 3.3.1 POAM list page behavior

- **File (template):** `poam/templates/poam/list.html` (to be created as part of POAM-specific feature work).
- **Key UI elements:**
  - Header: “Plan of Actions and Milestones”.
  - Tabs or pill-style filters:
    - `Open` – default tab, shows entries with status `open`.
    - `Closed` – shows entries with status `closed`.
  - Table of entries with at least:
    - POAM ID.
    - Status.
    - Owner.
    - Source and/or related enclave names (if available).
    - Due date.
  - Action area:
    - “Add POAM entry” button: navigates to create/edit page.
    - Future: link to bulk import/export if needed.
- **Data source:**
  - Initially driven by in-memory/sample data or a future `list-poam-entries` query.
  - The UI layout should assume that each entry’s shape is compatible with the `create-poam-entry` fields (see Section 4).

#### 3.3.2 POAM create/edit page behavior

- **File (template):** `poam/templates/poam/edit.html` (or similar).
- **Use backend contract:** `backend/existing-state/contracts/operations/create-poam-entry.yaml`.
  - Required fields:
    - `operation: create-poam-entry`.
    - `mode: verify | modify`.
    - `poam_id` (string).
    - `status` (`open` | `closed`).
  - Optional fields (map to form inputs as appropriate):
    - `source`, `enclave_ids`, `enclave_names`, `vulnerability_ids`, `observation`, `plan`, `owner`, `create_date`, `due_date`, `completion_date`, `comments`, `sequence_number`, `resource_ids`.
- **Form layout:**
  - Split into logical sections:
    - **Identification:** POAM ID, status, owner, source.
    - **Context:** related enclave IDs/names, vulnerability IDs, resource IDs.
    - **Timeline:** create date, due date, completion date.
    - **Details:** observation, plan, comments.
  - Include `mode` selection:
    - Radio buttons or a select input for `verify` vs `modify` (default to `modify` for creation).
  - On submit:
    - Call the `create-poam-entry` Lambda via the `landing` or a dedicated app view, following the invocation contract.
    - Show success or error message in-page; return to POAM list or keep editing as appropriate.

### 3.4 Operations (with nested categories)

- **Section label:** `Operations`.
- Group operations into **nested categories** in the sidebar, each category being collapsible (Bootstrap collapse can be used):
  - Examples (subject to refinement as more operations are added):
    - **User Management**
      - `unlock-user` (common; should be visible even when the category is collapsed).
    - **Enclave Setup**
      - Operations that prepare enclaves or configure AD connectors.
    - **Image and AMI**
      - Operations like `share-ami` or similar image-related helpers.
    - **Maintenance / Utilities**
      - Less common helpers that are already part of pipelines or backend contracts.
- **Common vs less common operations:**
  - Common operations (such as `unlock-user`) should:
    - Appear near the top of the Operations section.
    - Be accessible with a single click (no extra expansion required).
  - Less common operations should:
    - Live inside expandable categories (`More image operations`, `Additional utilities`, etc.).
    - Remain discoverable but not overwhelm the sidebar.

#### 3.4.1 Operation navigation behavior

- Each operation nav item should:
  - Route to a central operation form view (e.g. `operations:detail` with `operation_id`) OR a dedicated form page.
  - Render the operation-specific inputs in the **central content pane**.
  - Use the **existing operation contracts** under `backend/existing-state/contracts/operations/` to drive:
    - Input fields (required vs optional).
    - Mode selections (e.g., `verify`, `modify`).
    - Invocation behavior and response handling.
- For quick operations (like `unlock-user`), the existing header **quick actions dropdown and modal** can remain available, but the sidebar entry should provide a full-page alternative view.

---

## 4. POAM operation: `create-poam-entry`

### 4.1 Contract summary

- **File:** `backend/existing-state/contracts/operations/create-poam-entry.yaml`.
- **Operation ID:** `create-poam-entry`.
- **Invocation:**
  - Target: `SreManagementFunction`.
  - Method: `lambda.invoke` with `InvocationType="RequestResponse"`.
  - Payload:
    - Required:
      - `operation: create-poam-entry`.
      - `mode: verify | modify`.
      - `poam_id: string`.
      - `status: open | closed`.
    - Optional:
      - `source: string`.
      - `enclave_ids: list[string]`.
      - `enclave_names: list[string]`.
      - `vulnerability_ids: list[string]`.
      - `observation: string`.
      - `plan: string`.
      - `owner: string`.
      - `create_date: string`.
      - `due_date: string`.
      - `completion_date: string`.
      - `comments: string`.
      - `sequence_number: string or number`.
      - `resource_ids: list[string]`.
  - Response:
    - Success: includes `status` and, depending on mode, `verified` or `poam_id` and `entry_status`.
    - Error: includes `status`, `error`, `message`.

### 4.2 Front-end usage expectations

- The POAM create/edit page(s) should:
  - Respect the required vs optional fields defined in the contract.
  - Construct request payloads exactly as specified.
  - Surface backend messages (success or error) without leaking internal details.
- The POAM list view should:
  - Be ready to work with a future `list-poam-entries` query that uses a compatible field set.
  - Allow basic open/closed filtering and navigation into edit views.

---

## 5. Contextual right-hand pane: Vulnerability Management

### 5.1 General pattern

- **Goal:** Make Vulnerability Management a **right-hand contextual pane** that can be reused across:
  - Enclave detail.
  - Endpoint detail.
- The pane should:
  - Slide in from or sit flush with the right-hand side of the central content area.
  - Be **toggleable** via a clearly labeled control (see Section 6).
  - Have its own internal scrolling for long tables.

### 5.2 Enclave detail page integration

- **File:** `endpoints/templates/endpoints/enclave_detail.html`.
- Current layout already uses a split row:
  - Left: endpoints table.
  - Right: inline vulnerabilities panel include.
- Update this layout to:
  - Treat the vulnerabilities section as a **right-hand contextual pane**.
  - Introduce container and classes such as:
    - `.context-layout` – wrapper for main content + right pane.
    - `.context-main` – primary content area (endpoints table).
    - `.context-pane` – right-hand pane wrapping `_vulnerabilities_panel.html`.
  - Support hidden/visible states:
    - When hidden: only the context toggle control is visible along the right side; endpoints table can take more width.
    - When visible: the pane appears, and the endpoints table adjusts to the remaining width.
- Reuse existing vulnerabilities panel partial:
  - `endpoints/templates/endpoints/_vulnerabilities_panel.html`.
  - No changes to backend data contract are required for this feature.

### 5.3 Endpoint detail page integration

- **File:** `endpoints/templates/endpoints/endpoint_detail.html`.
- Update the endpoint detail layout to:
  - Wrap existing sections (breadcrumb, session manager card, operations cards, provisioning card) in a **central content container** that can share a right-hand pane.
  - Add a right-hand contextual pane region that:
    - Reuses the `_vulnerabilities_panel.html` partial when vulnerability data is available for that endpoint.
    - Otherwise shows an explanatory stub (e.g., “Vulnerability data is not yet available for this endpoint.”) or remains hidden.
  - Use the same `.context-layout`, `.context-main`, and `.context-pane` pattern as the enclave detail page so behavior is consistent.

### 5.4 Behavior and state

- **Default state:**
  - For users with no prior preference, the Vulnerability Management pane should start **closed**.
- **Per-page behavior:**
  - The open/closed state should be managed separately for:
    - Enclave detail pages.
    - Endpoint detail pages.
- **Persistence (optional, but recommended):**
  - Use `localStorage` keys to remember user preference:
    - Example keys:
      - `sreConsole.vulnPaneOpen.enclave` – boolean-like flag for enclave detail pages.
      - `sreConsole.vulnPaneOpen.endpoint` – boolean-like flag for endpoint detail pages.
  - On page load:
    - Read the appropriate key.
    - Apply open/closed classes to the contextual pane and update the toggle control state.

---

## 6. Toggle control for Vulnerability Management pane

### 6.1 Visual design

- Implement a **vertical tab or icon strip** anchored along the right edge of the central content area:
  - Contains the text **“Vulnerability Management”** rendered vertically.
  - Should clearly indicate that activating it will open or close the vulnerability pane.
  - When the pane is open, the toggle should visually indicate the active state (e.g. different background or border).
- Ensure the toggle is visible even when the pane is closed, so the user always has a way to reveal the pane.

### 6.2 Interaction and accessibility

- Implement the toggle control as a **button** element:
  - Use `aria-controls` to reference the contextual pane container.
  - Use `aria-expanded="true|false"` to reflect open/closed state.
  - Include an accessible label, such as:
    - `aria-label="Toggle Vulnerability Management pane"`.
- Behavior:
  - Clicking the control:
    - Toggles open/closed classes on the contextual pane container.
    - Updates `aria-expanded`.
    - Updates stored preference in `localStorage` when supported.
  - Keyboard:
    - Ensure the control is reachable via `Tab` order.
    - Pressing `Enter` or `Space` should toggle it, consistent with button semantics.

---

## 7. Accessibility and responsive behavior

### 7.1 Left-hand navigation

- Use a semantic `<nav>` element for the sidebar, with:
  - `aria-label="Primary"` (or similar) to describe its role.
  - Clear, high-contrast styling for active and focused items.
- Preserve intuitive focus order:
  - Header and skip link first.
  - Then sidebar navigation.
  - Then main content and contextual pane controls.
- Ensure the sidebar remains usable:
  - When collapsed on small screens, the toggle should itself be focusable and labeled.

### 7.2 Contextual pane

- The Vulnerability Management pane content should:
  - Remain in the DOM when hidden (for screen readers) unless explicitly collapsed with `aria-hidden` and `hidden` attributes.
  - Use appropriate headings and landmark roles so that screen readers can navigate within it.
- When toggling:
  - Avoid sudden focus jumps that disorient users.
  - If necessary, move focus into the pane only when it is the user’s explicit next destination (e.g. after opening from keyboard).

### 7.3 Responsive layout

- On **large** screens:
  - Display left nav, central content, and right pane side by side when the pane is open.
  - Ensure tables (endpoints, vulnerabilities) have independent scroll when they grow tall.
- On **small** screens:
  - Stack the regions vertically in a sensible order, for example:
    1. Header (with nav toggle).
    2. Sidebar (when expanded).
    3. Main content.
    4. Vulnerability pane (when opened via its toggle).
  - Allow the vulnerability toggle to scroll with content, staying discoverable.

---

## 8. Testing and documentation

- **Testing expectations**
  - Navigating via the left-hand nav:
    - `Workflows` → landing dashboard.
    - `Endpoint Management` → endpoints index.
    - `Plan of Actions and Milestones` → POAM list page.
    - `Operations` nested items → operation-specific central forms.
  - Toggling the Vulnerability Management pane:
    - Works on both Enclave detail and Endpoint detail.
    - Respects default closed state for new sessions.
    - Persists user preference when `localStorage` is available.
  - Layout remains usable and readable on narrow viewports.
- **Documentation**
  - Update `README.md` with:
    - A short description of the new shell layout and navigation.
    - A brief explanation of contextual panes (starting with Vulnerability Management).
  - Optionally add a small diagram (e.g., mermaid) to show shell regions in developer docs if helpful.

