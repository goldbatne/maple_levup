'use strict';
// Read-only source-structure regression, NOT a Maker/RPC runtime certification.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../../..');
const portalPath = 'RootDesk/MyDesk/Room/RoomPortal.mlua';
const noticePath = 'RootDesk/MyDesk/UI/GateNotice.mlua';
const portal = fs.readFileSync(path.join(root, portalPath), 'utf8');
const notice = fs.readFileSync(path.join(root, noticePath), 'utf8');

function method(source, name) {
  const expression = new RegExp('^    method [^\\n]+ ' + name + '\\([^\\n]*\\)\\r?\\n([\\s\\S]*?)^    end\\s*$', 'm');
  const match = source.match(expression);
  assert.ok(match, 'Required method missing: ' + name);
  return match[1];
}
function verify(portalSource, noticeSource) {
  const tryPass = method(portalSource, 'TryPass');
  const canPass = method(portalSource, 'CanPass');
  const rpc = method(noticeSource, 'ShowGateBlocked');
  assert.match(noticeSource, /@Logic\s+script GateNotice extends Logic/);
  assert.match(noticeSource, /@ExecSpace\("Client"\)\s+method void ShowGateBlocked\(string roomId, string reason\)/);
  assert.match(rpc, /self:Show\(reason\)/);
  assert.doesNotMatch(portalSource, /self:ShowGateBlocked\(|method void ShowGateBlocked\(/);
  assert.equal((portalSource.match(/_GateNotice:ShowGateBlocked\(/g) || []).length, 2);
  assert.match(tryPass, /_GateNotice:ShowGateBlocked\(targetRoomId,\s*"[^"\n]+", userId\)/);
  assert.match(canPass, /_GateNotice:ShowGateBlocked\(targetRoom.id, gate.reason, player.PlayerComponent.UserId\)/);
  const attempt = tryPass.indexOf('_GameData:TryBeginRogueliteTransition(');
  const firstLockGuard = tryPass.indexOf('if _GameData.RogueTransitionLocked then return end');
  assert.ok(firstLockGuard >= 0 && firstLockGuard < attempt, 'Duplicate-transition guard must precede transition attempt');
  const failedBranch = tryPass.slice(attempt, tryPass.indexOf('_GateNotice:ShowGateBlocked('));
  assert.match(failedBranch, /if _GameData.RogueTransitionLocked then return end/);
  assert.match(failedBranch, /if not isvalid\(player\) or player.CurrentMap ~= currentMap then return end/);
  assert.match(tryPass, /_TeleportService:TeleportToMapPosition\(runPlayer, arrive, targetRoom.map_name\)/);
  assert.match(tryPass, /_GameData:ReviveRunSpectatorsAtTransition\(targetRoomId, arrive\)/);
}
verify(portal, notice);
const negativeCases = [
  () => verify(portal.replace('_GateNotice:ShowGateBlocked(', 'self:ShowGateBlocked('), notice),
  () => verify(portal, notice.replace('@ExecSpace("Client")', '@ExecSpace("ClientOnly")')),
  () => verify(portal.replaceAll('if _GameData.RogueTransitionLocked then return end', ''), notice),
  () => verify(portal.replace(', userId)', ', "not-a-user")'), notice)
];
for (const negative of negativeCases) assert.throws(negative);
console.log(JSON.stringify({status: 'PASS_STATIC', scope: 'actual source RPC ownership/routing, transition-guard structure', files: [portalPath, noticePath], negativeTests: negativeCases.length, runtime: 'NOT_RUN', writes: false}, null, 2));
