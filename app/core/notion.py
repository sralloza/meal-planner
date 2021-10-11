from typing import Dict, List

import requests

from .config import settings


def create_notion_block(content: str, bold=False, italics=False, code=False):
    block = {
        "type": "text",
        "text": {"content": content},
        "annotations": {},
    }
    if bold:
        block["annotations"]["bold"] = True
    if italics:
        block["annotations"]["italics"] = True
    if code:
        block["annotations"]["code"] = True
    if not bold and not italics and not code:
        del block["annotations"]

    return block


def update_notion_text(blocks: List[Dict]):
    headers = {
        "Authorization": f"Bearer {settings.NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }

    response = requests.patch(
        f"https://api.notion.com/v1/blocks/{settings.NOTION_BLOCK_ID}",
        json={"type": "paragraph", "paragraph": {"text": blocks}},
        headers=headers,
    )
    response.raise_for_status()
