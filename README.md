# v-backtester

## Setup

step 1. enable claude code agent team setting
- https://youtu.be/Jxp3ruMdKxY?si=ePIGzU1U23xeer3v&t=291
- https://code.claude.com/docs/en/agent-teams#enable-agent-teams

- `open ~/.claude`

- update `settings.json` as below:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true,
    "us-stock-analysis@invest-skill": true
  },
  "extraKnownMarketplaces": {
    "everything-claude-code": {
      "source": {
        "source": "github",
        "repo": "affaan-m/everything-claude-code"
      }
    }
  },
  "feedbackSurveyState": {
    "lastShownTime": 1754277421728
  }
}
```


step 2. run below prompt in project in claude CLI
step 3. ask QA agent test, validte the project

## Ref

- Claude code Agent Teams
  - https://code.claude.com/docs/en/agent-teams
- LargitData - 大數軟體 (example:BackTester - 投資回測系統)
  - 完整影片教學: https://www.largitdata.com/course/258/
  - 程式碼: https://github.com/ywchiu/vibe-backtester
