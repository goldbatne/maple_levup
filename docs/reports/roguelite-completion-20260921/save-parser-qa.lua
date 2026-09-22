-- Pure parser tests only: no DataStorage write/read, no player state mutation.
local p=_UserService.UserEntities.Values[1]
local db=p:GetComponent('script.PlayerDBManager')
local tests={
 {'missingFields','{"schema_version":1}',false,true},
 {'malformed','{broken',false,false},
 {'futureSchema','{"schema_version":999}',false,false},
 {'wrongRoot','[]',false,false},
 {'wrongContainer','{"schema_version":1,"area_clears":4}',false,false},
 {'wrongCount','{"schema_version":1,"area_clears":{"area_00":"4"}}',false,false},
 {'negativeCount','{"schema_version":1,"area_clears":{"area_00":-1}}',false,false},
 {'fractionCount','{"schema_version":1,"area_clears":{"area_00":1.5}}',false,false},
 {'wrongDiscovery','{"schema_version":1,"discovered_abilities":{"s_mon_slime":{}}}',false,false},
 {'wrongSettings','{"schema_version":1,"settings":{"key_order":3}}',false,false},
 {'valid','{"schema_version":1,"area_clears":{"area_00":4},"discovered_abilities":{"s_mon_slime":1},"settings":{"key_order":"Q,W,E,R,T"}}',false,true},
 {'legacyNoRogue','{"Level":200}',true,true},
 {'legacyRogue','{"RoguelitePermanent":{"area_clears":{"area_00":2}}}',true,true},
 {'legacyWrong','{"RoguelitePermanent":2}',true,false}
}
local failed=0
for _,t in ipairs(tests) do
 local ok,result=pcall(function() return db:DecodeRogueliteRecord(t[2],t[3]) end)
 local accepted=ok and result~=nil
 local pass=ok and accepted==t[4]
 if not pass then failed+=1 end
 log('[AuditSaveParser] '..t[1]..' accepted='..tostring(accepted)..' expected='..tostring(t[4])..' pass='..tostring(pass))
end
log('[AuditSaveParser] DONE total='..#tests..' failed='..failed..' storageCalls=0')
