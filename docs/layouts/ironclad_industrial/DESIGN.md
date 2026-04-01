# Design System Specification: Industrial Intelligence

## 1. Overview & Creative North Star
**Creative North Star: The Sovereign Operator**

This design system moves beyond the "utilitarian dashboard" to create a premium, authoritative command environment. It rejects the clutter of traditional industrial software in favor of **Organic Brutalism**—a style that marries the heavy, reliable physical presence of factory machinery with a sophisticated, high-end digital editorial layer. 

By leveraging intentional asymmetry and high-contrast tonal layering, we move away from "templates" toward a bespoke signature experience. The layout communicates absolute reliability and high-stakes precision, ensuring that critical production data isn't just displayed, but is *staged* with cinematic clarity.

---

## 2. Colors: Tonal Depth & Industrial Soul
The palette is rooted in a deep, authoritative Industrial Blue (`primary: #002a4d`), inspired by heritage manufacturing. Rather than using flat blocks of color, we utilize the depth of the Material palette to create a sense of environment.

*   **Primary & Branding:** Use `primary` for global navigation and core actions. To provide "soul," use a subtle linear gradient from `primary` (#002a4d) to `primary_container` (#1b4066) on large surfaces like hero headers or primary action sidebars.
*   **The "No-Line" Rule:** 1px solid borders for sectioning are strictly prohibited. Boundaries are defined solely through background shifts. For example, a sidebar using `surface_container_low` sits flush against a main content area using `surface`.
*   **Surface Hierarchy:** 
    *   **Base:** `surface` (#f4faff)
    *   **Sub-sections:** `surface_container` (#e3f0f8)
    *   **Active/Elevated Modules:** `surface_container_lowest` (#ffffff)
*   **The Glass & Gradient Rule:** For overlay menus or floating machine status modals, use Glassmorphism. Apply `surface_container_lowest` at 85% opacity with a `backdrop-blur: 20px`. This integrates the UI with the layers beneath it, preventing a "pasted on" look.

---

## 3. Typography: Authoritative Clarity
We use **Inter** to bridge the gap between technical legibility and modern editorial sophistication. The scale is intentionally oversized to ensure glanceability from 3–5 feet away on the factory floor.

*   **Display & Headline (The Bold Statement):** Use `display-lg` and `headline-lg` for critical machine metrics (e.g., RPM, Temperature). These should feel like physical readouts—bold, heavy, and impossible to miss.
*   **Title (The Narrative):** `title-lg` is reserved for card headers and section titles. It provides the "Editorial" feel, acting as a clear anchor for the eye.
*   **Body (The Precision):** `body-lg` (1rem) is our minimum for any functional text. In an industrial context, "Small" is a failure state.
*   **Labels (The Metadata):** Use `label-md` in all-caps with a 0.05em letter spacing for secondary data like timestamps or unit measurements (e.g., "KG/HR").

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too "web-standard" for this system. We convey hierarchy through physical stacking logic.

*   **The Layering Principle:** Depth is achieved by "stacking" surface tiers. Place a `surface_container_lowest` card on a `surface_container_low` background to create a soft, natural lift.
*   **Ambient Shadows:** For floating elements (like an active machine control panel), use an extra-diffused shadow: `box-shadow: 0 20px 50px rgba(17, 29, 35, 0.06)`. Note the tinting—the shadow is a low-opacity version of `on_surface` (#111d23), never pure black.
*   **The "Ghost Border" Fallback:** If high-glare environments require more definition, use a "Ghost Border": `outline_variant` at 15% opacity. Never use 100% opaque lines.
*   **Intervention State:** When a machine enters an error state, the surface does not just turn red; the entire container shifts to `error_container` with a `surface_bright` inner glow to signify "Energy" and "Alert."

---

## 5. Components: Robust & Tactile

### Buttons
*   **Primary:** Height: `spacing.10` (3.5rem/56px). Background: `primary`. Border-radius: `roundedness.md` (0.375rem).
*   **Stateful Borders:** When a button is "Active" or "Focused," use a 3px solid border using `on_primary_fixed_variant`. This adds a "thick" tactile feel reminiscent of physical industrial switches.

### Production Cards
*   **Style:** Forbid divider lines. Use `spacing.4` (1.4rem) of vertical white space to separate data points.
*   **Layout:** Use asymmetrical layouts—place the primary metric (`display-sm`) in the top left and the status indicator in the bottom right to break the standard grid and guide the eye diagonally.

### Status Indicators (Machine Health)
*   **Online:** `tertiary_fixed_dim` dot with a pulse animation.
*   **Offline:** `outline` dot.
*   **Warning:** `on_secondary_container` (Yellow/Orange) icon with a high-contrast `on_surface` background.

### Input Fields
*   **Industrial Style:** Use a "filled" variant with `surface_container_high`. Upon focus, the bottom border should animate to 3px thickness using `primary`. Label text must never shrink below `label-md`.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical spacing. A wider left margin than right margin can create a more "designed," editorial look.
*   **Do** use "surface-on-surface" nesting to define modules.
*   **Do** use `tertiary` (#00300b) for success states; it is a sophisticated, "British Racing Green" variant that feels more premium than standard lime green.
*   **Do** ensure every touch target is at least 48px by 48px to accommodate gloved hands.

### Don't
*   **Don't** use 1px solid dividers. Use `spacing.6` (2rem) or background color shifts instead.
*   **Don't** use pure black (#000000). Use `on_background` (#111d23) for all "black" text to maintain tonal harmony with the industrial blue.
*   **Don't** use standard "drop shadows." If it doesn't look like ambient light, don't use it.
*   **Don't** clutter the screen. If a piece of data isn't vital for the next 30 seconds of operation, move it to a secondary layer.