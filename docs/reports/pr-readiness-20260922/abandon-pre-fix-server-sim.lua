-- Exact production function bodies; fake identities/services only. Not multiplayer Runtime.
local _UserService = {GetUserEntityByUserId=function(self,id) return nil end}
local _TimerService = {SetTimerOnce=function(self,fn,delay) return 0 end}
local function CheckRogueliteRunFailure(self)
        if self.RogueRunActive == false or self.RogueRunComplete or self.RogueRunFailed
            or self.RogueRunResult ~= "ACTIVE" then return false end
        for i = 1, #self.RogueParticipantIds do
            if self.RogueAliveParticipants[self.RogueParticipantIds[i]] == true then return false end
        end
        self.RogueRunFailed = true
        self.RogueRunResult = "FAILED"
        self.RogueDamageSummary = self:BuildRunDamageSummary()
        self:BroadcastRogueliteView()
        log("[RogueRun] FAILED — 전원 사망/이탈")
        local failedRevision = self.RogueRunRevision
        _TimerService:SetTimerOnce(function()
            if failedRevision ~= self.RogueRunRevision then return end
            for i = 1, #self.RogueParticipantIds do
                local player = _UserService:GetUserEntityByUserId(self.RogueParticipantIds[i])
                if isvalid(player) then
                    ---@type PlayerSkillSlots
                    local slots = player:GetComponent("script.PlayerSkillSlots")
                    if slots ~= nil then
                        slots:EndRogueliteRun()
                    end
                end
            end
            self:ReturnRogueliteParticipantsToLobby()
        end, 3)
        return true
end
local function AbandonRogueliteParticipant(self,userId)
        if userId == nil or userId == "" then return false end
        if self.RogueRunActive == false or self.RogueRunComplete or self.RogueRunFailed
            or self.RogueRunResult ~= "ACTIVE" then
            log_warning("[RogueAbandon] 이미 확정된 Run 요청 무시 user=" .. tostring(userId)
                .. " result=" .. tostring(self.RogueRunResult))
            return false
        end
        if self:IsRunParticipant(userId) == false then
            log_warning("[RogueAbandon] 참가자가 아닌 요청 차단 user=" .. tostring(userId))
            return false
        end

        -- 서버의 한 실행 흐름에서 먼저 원장에서 제외한다. 이후 같은 프레임에 Boss가
        -- 죽어도 CompleteRogueliteRun의 보상/기록 대상에 이 사용자는 들어가지 않는다.
        self.RogueParticipantResults[userId] = "ABANDONED"
        self.RogueAliveParticipants[userId] = nil
        self.RogueDisconnectedAt[userId] = nil
        self.RogueDamageLedger[userId] = nil
        local remaining = {}
        for i = 1, #self.RogueParticipantIds do
            if self.RogueParticipantIds[i] ~= userId then
                remaining[#remaining + 1] = self.RogueParticipantIds[i]
            end
        end
        self.RogueParticipantIds = remaining

        local player = _UserService:GetUserEntityByUserId(userId)
        local hasPlayer = isvalid(player)
        if hasPlayer then
            self:CleanupAbandonedRunPlayer(player)
            self:NotifyRogueAbandonAccepted(userId)
        end

        if #self.RogueParticipantIds == 0 then
            -- 모든 참가자가 이탈한 경우에만 공유 Run을 닫는다. 남은 참가자가 있으면
            -- Graph/Encounter/Boss는 그대로 두고 그들의 Run은 계속된다.
            self.RogueRunResult = "ABANDONED"
            self.RogueRunActive = false
            self.RogueRunRevision += 1
            self.RogueTransitionLocked = false
            self:StopRogueliteRunSchedulers()
            self:ClearAbandonedRogueliteRunState()
        else
            self:BroadcastRogueliteView()
        end

        local moved = 0
        if hasPlayer then
            moved = _RoomService:MoveUsersToStaticRoom({ userId }, "maptown") or 0
            if moved < 1 and Environment:IsMakerPlay() then
                -- Maker local instance fallback은 중첩 Room 이동을 지원하지 않을 수 있다.
                _TeleportService:TeleportToMapPosition(player, Vector3(0, 0, 0), "maptown")
            end
        end
        log("[RogueAbandon] ABANDONED user=" .. userId
            .. " remaining=" .. tostring(#self.RogueParticipantIds)
            .. " moved=" .. tostring(moved))
        return true
end
local cases={{name="last_alive_leaves",ids={"QA_A","QA_B"},alive={QA_A=true,QA_B=false},expected="FAILED"},{name="survivor_remains",ids={"QA_A","QA_B"},alive={QA_A=true,QA_B=true},expected="ACTIVE"},{name="solo_leaves",ids={"QA_A"},alive={QA_A=true},expected="ABANDONED"}}
for _,c in ipairs(cases) do
 local s={RogueRunActive=true,RogueRunComplete=false,RogueRunFailed=false,RogueRunResult="ACTIVE",RogueParticipantResults={},RogueAliveParticipants=c.alive,RogueDisconnectedAt={},RogueDamageLedger={},RogueParticipantIds=c.ids,RogueRunRevision=1}
 function s:IsRunParticipant(id) for _,v in ipairs(self.RogueParticipantIds) do if id==v then return true end end return false end
 function s:BroadcastRogueliteView() end
 function s:BuildRunDamageSummary() return "QA" end
 function s:StopRogueliteRunSchedulers() end
 function s:ClearAbandonedRogueliteRunState() end
 s.CheckRogueliteRunFailure=CheckRogueliteRunFailure
 AbandonRogueliteParticipant(s,"QA_A")
 log("[PRQA] ABANDON_SERVER_SIM case="..c.name.." expected="..c.expected.." actual="..s.RogueRunResult.." pass="..tostring(c.expected==s.RogueRunResult))
end
