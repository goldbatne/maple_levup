# Actual multiplayer execution environment

Checked 2026-09-21. Status: **BLOCKED_RUNTIME_MULTIPLAYER in the currently connected tool environment**, not a claim that MSW cannot support multiplayer.

- Maker MCP exposes one `maker_play` endpoint (no player-count/client-launch argument) and one input/screenshot endpoint. All 17 Maker tool descriptions were inspected.
- `maker_get_context_keys` observed one `client`, `server_main`, and the active `server_instance_*`. Instance servers are not independent player clients.
- No connected tool for launching a second authenticated MSW player client was found. Native computer automation is disabled in this session. No additional authenticated player sessions are provided.
- Official document retrieval was actually queried for multi-client/test-player launch; returned release/start-position/server-client guides, not a callable multi-client Maker control.
- Alternative confirmed in [official World Release guide](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1321): private release and group-member testing. Publication and additional users/accounts are external coordination, not an authorized local QA shortcut. No release was performed.
- 1–4 participant HP function output was tested on the Maker server as 1.00/1.25/1.50/1.75. This is **SERVER_SIM**, not 2P/3P/4P runtime certification.

Independent-client synchronization, concurrent UI/ability choice, spectator/rejoin/disconnect behavior remain unverified in actual multiplayer. Static/server tests must keep separate result labels.
