box.cfg{
    listen = 3301,
    memtx_memory = 4 * 1024 * 1024 * 1024,
}

box.schema.user.grant('guest', 'read,write,execute', 'universe', nil, {if_not_exists = true})

box.schema.create_space('kv', {
    if_not_exists = true,
    format = {
        {name = 'key', type = 'string'},
        {name = 'value', type = 'string'},
    },
})
box.space.kv:create_index('primary', {parts = {'key'}, if_not_exists = true})

box.schema.create_space('doc', {
    if_not_exists = true,
    format = {
        {name = 'key', type = 'string'},
        {name = 'doc', type = 'map'},
    },
})
box.space.doc:create_index('primary', {parts = {'key'}, if_not_exists = true})

box.schema.create_space('queue', {
    if_not_exists = true,
    format = {
        {name = 'qkey', type = 'string'},
        {name = 'id', type = 'unsigned'},
        {name = 'msg', type = 'map'},
    },
})
box.space.queue:create_index('primary', {parts = {'qkey', 'id'}, if_not_exists = true})

function queue_pop(qkey)
    local t = box.space.queue.index.primary:min({qkey})
    if t ~= nil then
        box.space.queue:delete({qkey, t[2]})
    end
    return t
end

function doc_get_field(key, field)
    local t = box.space.doc:get(key)
    if t == nil then
        return nil
    end
    return t.doc[field]
end