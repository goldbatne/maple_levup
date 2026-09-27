if not Environment:IsMakerPlay() then return end
for _, id in ipairs({"s_mon_memory_monk_trainee", "s_mon_official_knight_c"}) do
    local skill = _GameData:GetSkill(id)
    if skill == nil then
        log_warning("[SkillVFXQA] DATA_MISSING " .. id)
    else
        local layers = skill.effect_layers or {}
        local layer = layers[1]
        log("[SkillVFXQA] DATA id=" .. id
            .. " layers=" .. tostring(#layers)
            .. " frames=" .. tostring(layer and #layer.frame_ruids or -1)
            .. " duration=" .. tostring(layer and layer.duration or -1)
            .. " offsetY=" .. tostring(layer and layer.offset_y or -1))
    end
end
