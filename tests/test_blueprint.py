import pathlib
import re
import unittest
from jinja2 import Environment, StrictUndefined
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "blueprints" / "automation" / "fluentpet_alexa_voice_replay.yaml"

class BlueprintInput(str):
    pass

class BlueprintLoader(yaml.SafeLoader):
    pass

def input_constructor(loader, node):
    return BlueprintInput(loader.construct_scalar(node))

BlueprintLoader.add_constructor("!input", input_constructor)

with BLUEPRINT_PATH.open(encoding="utf-8") as f:
    SOURCE = f.read()
BLUEPRINT = yaml.load(SOURCE, Loader=BlueprintLoader)


def get_input_keys():
    output = {}
    for key, value in BLUEPRINT["blueprint"]["input"].items():
        if isinstance(value, dict) and "input" in value:
            output.update(value["input"])
        else:
            output[key] = value
    return output


def all_input_refs(tree):
    if isinstance(tree, BlueprintInput):
        return [str(tree)]
    if isinstance(tree, dict):
        return [ref for k, v in tree.items() for ref in all_input_refs(k) + all_input_refs(v)]
    if isinstance(tree, list):
        return [ref for v in tree for ref in all_input_refs(v)]
    return []


class TestBlueprint(unittest.TestCase):
    def test_blueprint_schema(self):
        self.assertEqual(BLUEPRINT["blueprint"]["domain"], "automation")
        self.assertEqual(BLUEPRINT["blueprint"]["homeassistant"]["min_version"], "2026.10.0")
        self.assertEqual(BLUEPRINT["mode"], "queued")
        self.assertEqual(BLUEPRINT["triggers"][0]["trigger"], "state")
        self.assertIn("to", BLUEPRINT["triggers"][0])
        self.assertIsNone(BLUEPRINT["triggers"][0]["to"])
        self.assertEqual(BLUEPRINT["actions"][0]["action"], "notify.send_message")
        self.assertIn("delay", BLUEPRINT["actions"][1])

    def test_inputs_defined(self):
        inputs = get_input_keys()
        refs = set(all_input_refs(BLUEPRINT))
        self.assertTrue(refs)
        self.assertEqual(refs, set(inputs), f"Unused or undefined !input refs: {refs ^ set(inputs)}")
        self.assertEqual(inputs["fluentpet_buttons"]["selector"]["entity"]["multiple"], True)
        self.assertEqual(inputs["fluentpet_buttons"]["selector"]["entity"]["filter"][0]["integration"], "fluentpet")
        self.assertEqual(inputs["alexa_targets"]["selector"]["target"]["entity"][0]["domain"], "notify")
        self.assertEqual(inputs["audio_base_url"]["selector"]["text"]["type"], "url")

    def test_no_private_household_content(self):
        self.assertNotIn("nabu.casa", SOURCE)
        self.assertNotIn("pngbbtk", SOURCE)
        self.assertNotIn("notify.kitchen_kitchen_echo_speak", SOURCE)
        self.assertNotIn("FLUENT4654", SOURCE)

    def test_dynamic_filename(self):
        message = BLUEPRINT["actions"][0]["data"]["message"]
        env = Environment(undefined=StrictUndefined)
        template = env.from_string(message)
        prefix = "FluentPet_"
        suffix = ".mp3"
        base = "https://example.org/local/fluentpet/"
        cases = {
            "Daddy": "FluentPet_Daddy.mp3",
            "Mommy": "FluentPet_Mommy.mp3",
            "Love You": "FluentPet_Love_You.mp3",
            "All Done": "FluentPet_All_Done.mp3",
            "Watch TV": "FluentPet_Watch_TV.mp3",
            "Walk2": "FluentPet_Walk2.mp3",
        }
        for name, expected_file in cases.items():
            with self.subTest(button=name):
                rendered = template.render(
                    trigger={"to_state": {"attributes": {"button": {"name": name}}}},
                    audio_base_url=base,
                    filename_prefix=prefix,
                    filename_suffix=suffix,
                )
                # HA provides the urlencode filter; Jinja's built-in filters do too.
                self.assertEqual(rendered, f'<audio src="https://example.org/local/fluentpet/{expected_file}"/>')
                self.assertEqual(rendered.count("<audio src="), 1)

    def test_replay_protection(self):
        condition = BLUEPRINT["conditions"][0]["value_template"]
        env = Environment(undefined=StrictUndefined)
        template = env.from_string(condition)
        def render(event_type="press", replayed=False, name="Daddy"):
            return template.render(trigger={"to_state": {"attributes": {
                "event_type": event_type, "replayed": replayed, "button": {"name": name}
            }}}).strip().lower()
        self.assertEqual(render(), "true")
        self.assertEqual(render(replayed=True), "false")
        self.assertEqual(render(event_type="other"), "false")
        self.assertEqual(render(name=""), "false")

    def test_example_inputs(self):
        # Ensures the example is illustrative and does not copy the user's private URL.
        example = yaml.safe_load((ROOT / "examples/example_automation.yaml").read_text())
        inp = example[0]["use_blueprint"]["input"]
        self.assertIn("label_id", inp["alexa_targets"])
        self.assertEqual(inp["filename_prefix"], "FluentPet_")
        self.assertIn("your-domain.example", inp["audio_base_url"])


if __name__ == "__main__":
    unittest.main()
