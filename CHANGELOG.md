# Changelog

## 0.1.0 — 2026-11-12

- Initial Home Assistant blueprint for selected FluentPet Press event entities.
- Dynamic recorded audio URL using `FluentPet_<button_name>.mp3`.
- Configurable Alexa Speak targets, including Home Assistant labels.
- Configurable audio base URL, prefix, suffix, and spacing.
- Ignore replayed events and attribute-only state updates.
- Add quickstart, example, tests, and public GitHub release package and dedication to Snickers (@puppersnickerdoodle).

### Field validation — 2026-11-12 (Pacific Time)

- Public GitHub blueprint import and creation of a new blueprint-based Home Assistant automation succeeded.
- Migrated the working household setup to the blueprint: 12 FluentPet Press event entities, an Alexa Speak label with six devices, dynamic `FluentPet_<Button_Name>.mp3` filenames, and a two-second inter-press delay.
- Disabled the former direct automation and retained it for rollback.
- **Real-world playback confirmed by the owner** after a Love You press. The Home Assistant trace shows the replay/press condition passed, Alexa `notify.send_message` received `FluentPet_Love_You.mp3`, and the run finished.
- GitHub Actions automated validation and live Home Assistant import had already passed.

**Scope:** A single live press-to-audio path was confirmed. Individual playback for all 12 buttons or all six Echo devices was not independently checked. No blueprint behavior changed in this documentation update.