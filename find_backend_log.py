import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Extract model and controller content from backend logs."
)
parser.add_argument(
    "log_path",
    help="Path to the backend transcript JSONL file"
)
args = parser.parse_args()

log_path = Path(args.log_path)

model_content = None
controller_content = None

with log_path.open("r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        idx = data.get("step_index")

        if idx == 230:
            for tc in data.get("tool_calls", []):
                if "app-setting.model.ts" in str(tc):
                    model_content = (
                        tc.get("args", {}).get("CodeContent")
                        or tc.get("args", {}).get("ReplacementContent")
                    )

        if idx == 281:
            content_str = data.get("content", "")
            if "app-settings.controller.ts" in content_str:
                for tc in data.get("tool_calls", []):
                    if "app-settings.controller.ts" in str(tc):
                        controller_content = (
                            tc.get("args", {}).get("CodeContent")
                            or tc.get("args", {}).get("ReplacementContent")
                        )

if model_content:
    Path("model_output.ts").write_text(
        model_content, encoding="utf-8"
    )

if controller_content:
    Path("controller_output.ts").write_text(
        controller_content, encoding="utf-8"
    )

print("Model content found:", model_content is not None)
print("Controller content found:", controller_content is not None)
