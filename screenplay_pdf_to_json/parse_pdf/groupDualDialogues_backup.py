from screenplay_pdf_to_json.utils import isCharacter
import json
import copy

LATEST_PAGE = -1
EPSILON = 3


def groupDualDialogues(script, pageStart):
    """Detects and groups dual dialogues"""

    newScript = []
    for page in script:
        if page["page"] < pageStart:
            continue
        newScript.append({"page": page["page"], "content": []})

        i = 0
        isDualDialogue = 0

        while i < len(page["content"]):
            content = page["content"][i]
            currentY = round(content["y"])
            segmentToAdd = [{
                "x": content["x"],
                "y": content["y"],
                "text": content["text"]
            }]

            nextContent = page["content"][i + 1] if i + 1 < len(page["content"]) else False

            prevContent = page["content"][i - 1] if i - 1 >= 0 else False

            previousIsCharacter = prevContent and isCharacter(prevContent)

            nextContentIsCharacter = nextContent and isCharacter(nextContent)

            # If current line and next line are character, and the previous line is not character (3 characters in a row are impossible)
            if not previousIsCharacter and isCharacter(content) and nextContentIsCharacter:
                isDualDialogue = 1

            # If next content is on the same line, and isDualDialogue > 0, then it's a dual dialogue
            if nextContent and currentY == nextContent["y"] and isDualDialogue > 0:
                character2ToAdd = {
                    "x": nextContent["x"],
                    "y": nextContent["y"],
                    "text": nextContent["text"]
                }

                if isDualDialogue <= 2:
                    newScript[-1]["content"].append({
                        "segment": segmentToAdd,
                        "character2": [character2ToAdd]
                    })
                else:
                    newScript[-1]["content"][-1]["segment"].append(segmentToAdd[0])
                    newScript[-1]["content"][-1]["character2"].append(character2ToAdd)
                i += 1
                isDualDialogue += 1

            # If content resides in a different y-axis, it's not part of a dual dialogue
            else:
                isDualDialogue = 0
                # Add content's y-axis as key and the content array index position as value
                newScript[-1]["content"].append({
                    "segment": segmentToAdd,
                    "character2": []  # Initialize an empty list for character2
                })
            i += 1

    newScript = stitchLastDialogue(newScript, pageStart)
    return newScript


def stitchLastDialogue(script, pageStart):
    """
    Detect the last line of a dual dialogue. This isn't detected by groupDualDialogues since
    a dialogue may be longer than the other, and therefore take up a different y value
    """
    currScript = []
    for page in script:
        if page["page"] < pageStart:
            continue
        currScript.append({"page": page["page"], "content": []})
        margin = -1
        for i, content in enumerate(page["content"]):
            # If margin > 0, then content is potentially a dual dialogue
            if margin > 0:
                currScriptLen = len(currScript[LATEST_PAGE]["content"]) - 1

                # Content might be the last line of dual dialogue or not
                if "character2" not in content and i > 0:
                    # Last line of a dual dialogue
                    if abs(content["segment"][0]["y"] - page["content"][i - 1]["segment"][LATEST_PAGE]["y"]) <= margin + EPSILON:
                        def getDiff(contentX, currX): return abs(
                            contentX - currX)

                        diffBetweenContentAndSegment = getDiff(
                            content["segment"][0]["x"], currScript[LATEST_PAGE]["content"][currScriptLen]["segment"][0]["x"])
                        diffBetweenContentAndCharacter2 = getDiff(
                            content["segment"][0]["x"], currScript[LATEST_PAGE]["content"][currScriptLen]["character2"][0]["x"]) if "character2" in currScript[LATEST_PAGE]["content"][currScriptLen] else -1

                        if diffBetweenContentAndSegment < diffBetweenContentAndCharacter2:
                            currScript[LATEST_PAGE]["content"][currScriptLen]["segment"].append(content["segment"][0])
                        else:
                            currScript[LATEST_PAGE]["content"][currScriptLen]["character2"].append(content["segment"][0])

                    # Not a dual dialogue. Skip this line!
                    else:
                        currScript[LATEST_PAGE]['content'].append(content)
                        margin = 0

                # Still a dual dialogue
                else:
                    currScript[LATEST_PAGE]["content"][currScriptLen]["segment"].append(content["segment"][0])

            # If no dual
            else:
                if "character2" in content:
                    # Margin between character head and the FIRST line of dialogue
                    margin = abs(page["content"][i + 1]["segment"][0]["y"] -
                                 content["segment"][LATEST_PAGE]["y"])
                    currScript[LATEST_PAGE]['content'].append(content)
                else:
                    currScript[LATEST_PAGE]['content'].append(content)

    return currScript
