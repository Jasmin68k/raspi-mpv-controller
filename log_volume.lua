-- Put this script in ~/.config/mpv/scripts/
-- Configure path for stored volume and mute states below
-- Run MPV with --script-opts=volumeid=NAMEFORTHISMPVINSTANCE --volume=$(cat /path/to/mpv_volume_NAMEFORTHISMPVINSTANCE.txt) --mute=$(cat /path/to/mpv_mute_NAMEFORTHISMPVINSTANCE.txt)

function log_volume() 
    local volumeid = mp.get_opt("volumeid")
    if volumeid then 
        local volume = mp.get_property("volume")
        local mute_state = mp.get_property("mute")

        -- Set path for volume and mute state
        local base_path = "/path/to/"
        local volume_filename = base_path .. "mpv_volume_" .. volumeid .. ".txt"
        local volume_file = io.open(volume_filename, "w") 
        if volume_file then 
            volume_file:write(volume) 
            volume_file:close() 
        end

        local mute_filename = base_path .. "mpv_mute_" .. volumeid .. ".txt"
        local mute_file = io.open(mute_filename, "w")
        if mute_file then
            mute_file:write(mute_state)
            mute_file:close()
        end
    end 
end 

mp.register_event("shutdown", log_volume)
