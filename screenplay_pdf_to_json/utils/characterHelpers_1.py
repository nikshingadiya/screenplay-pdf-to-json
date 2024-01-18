from sys import stderr
import  re
def isParenthetical(text):
    return "(" in text and ")" in text

def remove_symbols_and_quotes(text):
    # Remove symbols
    text_no_symbols = re.sub(r'[^\w\s]', '', text)

    # Remove double quotes
    text_no_quotes = text_no_symbols.replace('"', '')

    return text_no_quotes.strip()


def extractCharacter(currentContent):
    text = currentContent["text"].strip()

    if isParenthetical(text):
        modifier_start = text.find("(")
        modifier_end = text.find(")")

        if modifier_start < modifier_end:  # Check if parentheses are balanced
            modifier = text[modifier_start + 1:modifier_end].strip()
            character = (text[:modifier_start] + text[modifier_end + 1:]).strip()
        else:
            stderr.write(f"Unbalanced parentheses in: {text}\n")
            modifier = None
            character = text
    else:
        modifier = None
        character = text
    # print("character",character)
    character=remove_symbols_and_quotes(character)
        
    return {
        "character": character.strip(),
        "modifier": modifier,
    }

def isCharacter(currentContent):

    text = currentContent["text"].strip()
    characterNameEnum = ["(V.O)", "(O.S)", "CONT'D"]

   

    # Check if the text is parenthetical
    if isParenthetical(text):
        return False

    # Check for specific character name indicators
    for heading in characterNameEnum:
        if heading in text:
            print("raw_text",text)
            return True



    # Extract potential character name without modifier
    characterName = text.split("(")[0].strip() if "(" in text else text

    # Check if the character name is in uppercase and starts with an alphabet character
   

    # Check for certain patterns indicating non-character lines
  
    if any(x in text for x in ["--", "!", "?", "@", "%", "...", "THE END",","]):
        return False
    
    if not characterName.isupper() or not characterName[0].isalpha():
        return False
    # Check if the line ends with a hyphen or colon
    if text.endswith("-") or text.endswith(":") or text.endswith(","):
        return False

    # Check the x-coordinate to filter out lines near the left edge
    if currentContent["x"] < 150:
        return False

    return True
