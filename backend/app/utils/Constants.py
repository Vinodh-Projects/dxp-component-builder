from app.prompts.eds.block_prompt import DEFAULT_BLOCKS_CODE

# Simple mapping: short keys to enum members
MODEL_SELECTOR = {
    "GPT_3": "gpt-3.5-turbo",
    "GPT_4": "gpt-4",
    "GPT_4o": "gpt-4o",
    "O1_PREVIEW": "o1-preview",
    "O1_MINI": "o1-mini",
    "CLAUDE_3_5_SONNET": "claude-3.5-sonnet",
    "GEMINI_1_5_PRO": "gemini-1.5-pro"
}

AEM_BLOCK_COLLECTION_URL = "https://cdn.jsdelivr.net/gh/adobe/aem-block-collection@main"

DEFAULT_BLOCKS_LIST = "accordion,cards,carousel,columns,embed,footer,form,fragment,header,hero,modal,quote,search,table,tabs,video"