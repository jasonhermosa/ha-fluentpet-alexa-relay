# FluentPet Alexa Relay — FluentPet Button Audio → Alexa Speak

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fjasonhermosa%2Fha-fluentpet-alexa-relay%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Ffluentpet_alexa_voice_replay.yaml)

A **Home Assistant automation blueprint** that plays your **own recorded audio** on Alexa Echo devices whenever a **FluentPet Connect** button is pressed.

Choose FluentPet button entities, choose Alexa **Speak** destinations (including a Home Assistant label/group of speakers), enter an HTTPS audio folder, and you're done. No custom Python and no hardcoded household-specific URLs.

> **Status:** v0.1.0 — **field-tested on Home Assistant**. Public GitHub blueprint import, creation of a new blueprint-based automation, and live Alexa audio playback have been confirmed. This is an independent community project, not affiliated with FluentPet, Amazon, or Home Assistant.

## Dedicated to Snickers 🐾

I built this for **Snickers**, our mini Bernedoodle, so the words he presses on his FluentPet soundboard can be heard throughout the house. What started as a little project to help us understand him turned into something I hope other pets and their people can enjoy, too.

Follow Snickers and his button-pressing adventures on Instagram: **[@puppersnickerdoodle](https://www.instagram.com/puppersnickerdoodle/)**.

## What it does

- Listens to selected FluentPet Connect **Press** event entities.
- Ignores `replayed: true` catch-up events and non-press state updates.
- Dynamically derives the filename from the *FluentPet-reported button name*, not the Home Assistant entity's custom display name. Spaces become underscores.
- Sends Alexa-compatible SSML `<audio>` to selected **Alexa Devices Speak** notification entities using `notify.send_message`.
- Supports Home Assistant labels as speaker targets, so you can change speakers without editing the automation.
- Queues rapid presses with an adjustable gap (default 2 seconds). Amazon may still rate-limit audio sent to many Echo devices at once.

For example:

| FluentPet button name | Audio file |
| --- | --- |
| Daddy | `FluentPet_Daddy.mp3` |
| Mommy | `FluentPet_Mommy.mp3` |
| Love You | `FluentPet_Love_You.mp3` |
| Watch TV | `FluentPet_Watch_TV.mp3` |
| Walk2 | `FluentPet_Walk2.mp3` |

The prefix (`FluentPet_`) and suffix (`.mp3`) are configurable. The capitalization of the FluentPet button's name matters on case-sensitive file systems.

## Requirements

1. **Home Assistant 2026.10 or newer.**
2. [FluentPet Connect for Home Assistant](https://support.fluent.pet/connect/home-assistant/) configured and its Press entities available.
3. [Alexa Devices](https://www.home-assistant.io/integrations/alexa_devices/) configured with at least one **Speak** `notify` entity (not an Announce entity).
4. Alexa-compatible MP3s reachable over **public HTTPS without authentication**. Home Assistant's `/config/www/fluentpet/` files can be served at `https://YOUR_PUBLIC_HA_HOST/local/fluentpet/` if the URL is externally reachable. Your host URL must be supplied by **you** and is **never** included in this repository.

**MP3 format:** Amazon specifies MPEG-2 Layer III, 48 kbps, sample rate 16 kHz / 22.05 kHz / 24 kHz. The file must be short enough for Alexa SSML audio and reachable without a login. Convert with FFmpeg:

```bash
ffmpeg -i input.wav -ac 2 -codec:a libmp3lame -b:a 48k -ar 24000 -write_xing 0 FluentPet_Daddy.mp3
```

See [Amazon SSML audio requirements](https://developer.amazon.com/en-US/docs/alexa/custom-skills/speech-synthesis-markup-language-ssml-reference.html).

**Privacy:** Files hosted under a publicly reachable `/local/` URL can be downloaded by anyone who knows their URL. Don't put personal, confidential, or sensitive recordings there. Don't commit your audio, cloud URL, Home Assistant tokens, or Amazon credentials to this repository.

## Install

1. In Home Assistant go to **Settings → Automations & scenes → Blueprints → Import blueprint**.
2. Import this URL (or use the button at the top):

   `https://github.com/jasonhermosa/ha-fluentpet-alexa-relay/blob/main/blueprints/automation/fluentpet_alexa_voice_replay.yaml`

3. Select **Create automation**, then choose:
   - Your FluentPet **Press** event entities (multi-select).
   - Your Alexa Devices **Speak** entities or a Home Assistant label that contains them.
   - The **public HTTPS folder URL** containing your MP3 recordings (not a specific MP3).
   - Optional filename prefix/suffix and spacing between requests.
4. Save and enable the automation. Press a button and confirm the sound on an Echo.

If you use a label for destinations, create it under **Settings → Areas, labels & zones → Labels**, then assign it to **Alexa Speak notify entities**. The label can grow later without modifying the automation.

### Avoid duplicate audio

If you already have FluentPet automations that play audio on Alexa, **disable them before enabling this blueprint instance**. Otherwise, one press could trigger both automations. Keep the old automation as a rollback until you have tested the new one.

### File naming

Files are built as:

```
<AUDIO_FOLDER>/<PREFIX><FLUENTPET_BUTTON_NAME_WITH_SPACES_REPLACED_BY_UNDERSCORES><SUFFIX>
```

For example, if the button name is `Love You`, folder is `https://example.org/local/fluentpet/`, and the default prefix/suffix are used:

```
https://example.org/local/fluentpet/FluentPet_Love_You.mp3
```

Use `FluentPet_` only once, as the default **prefix**. Don't enter the full filename in the audio folder field.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Automation never triggers | FluentPet event entity selected; Base connected; FluentPet integration receives press events. |
| Trace shows a send, but Alexa says it cannot access a skill or audio | Test **one Speak entity** using the exact audio URL; check capitalization, MP3 encoding, HTTPS and anonymous access. |
| Multiple Echos fail intermittently | Amazon rate limiting. Reduce the selected targets or increase spacing. The spacing affects consecutive **button presses**, not the simultaneous fan-out to six speakers. |
| Sound plays twice | Check for a second automation still enabled for the same event entity. |
| Custom HA name doesn't match filename | The filename uses FluentPet's `button.name` attribute, **not** Home Assistant's friendly name. |
| No sound after uploading a replacement MP3 | Check encoding and the URL. A new filename can avoid caches of the old URL. |
| Replayed events aren't spoken | Expected: `replayed: true` events are skipped. |

You can isolate Alexa playback in **Developer tools → Actions**:

```yaml
action: notify.send_message
target:
  entity_id: notify.your_echo_speak
data:
  message: >-
    <audio src="https://example.org/local/fluentpet/FluentPet_Daddy.mp3"/>
```

## Development

Blueprint: [`blueprints/automation/fluentpet_alexa_voice_replay.yaml`](blueprints/automation/fluentpet_alexa_voice_replay.yaml)

Install development requirements and run tests:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests check YAML and `!input` references, selector shape, and naming/rendering for common button names. **They do not substitute for an actual Home Assistant import and a real Echo playback test.**

See [example automation](examples/example_automation.yaml), [changelog](CHANGELOG.md), and [license](LICENSE).

## Contributing and releases

This blueprint is maintained in the public [ha-fluentpet-alexa-relay repository](https://github.com/jasonhermosa/ha-fluentpet-alexa-relay). Please open an issue for bugs or ideas, and a pull request for proposed changes. The README's **Import Blueprint** badge links to the current blueprint on the `main` branch.

Run the tests before submitting changes. For production use, import the blueprint into Home Assistant and test with a single Echo before enabling additional speakers. Always disable older FluentPet-to-Alexa automations for the same buttons to avoid duplicate playback.

## Credit and support

Independent community blueprint built from a working FluentPet Connect → Home Assistant → Alexa Devices setup. This project is **not affiliated with, endorsed by, or supported by** FluentPet, Amazon, or the Open Home Foundation.

For FluentPet integration issues, follow [FluentPet's official instructions](https://support.fluent.pet/connect/home-assistant/). For this blueprint, please open a GitHub issue.