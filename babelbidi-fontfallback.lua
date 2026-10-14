-- babelbidi-fontfallback.lua
--
-- Missing-glyph fallback using Babel-resolved fonts for babelbidi.
--
-- Copyright (C) 2026 Amer Amikhteh
--
-- This file is part of the babelbidi package.
--
-- This work may be distributed and/or modified under the conditions of
-- the LaTeX Project Public License, either version 1.3c of the License,
-- or (at your option) any later version.
--
-- This work is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
--
-- The full license text is available at:
-- https://www.latex-project.org/lppl/
--
-- This work is maintained by Amer Amikhteh.
--
-- Version: 0.3.0
-- Date: 2026-10-14



local F = {relations = {}, contexts = {}, context_ids = {}}
local glyph, disc, math_node = node.id('glyph'), node.id('disc'), node.id('math')

function F.set(source, targets)
  local ordered, seen = {}, {[source] = true}
  for _, target in ipairs(targets) do
    if not seen[target] then
      ordered[#ordered + 1], seen[target] = target, true
    end
  end
  F.relations[source] = ordered
end

local function mapped_font(locale, source)
  local props = Babel.locale_props[locale]
  return props and props['/' .. source]
end

-- Capture the font IDs Babel has resolved for this NFSS selection. A context
-- attribute keeps selections distinct even if NFSS substitutes the same
-- physical source font for different requested weights or sizes. It also
-- follows the effective font after Babel's automatic onchar mapping.
function F.capture(source)
  local routes, key = {}, {source}
  for locale, targets in pairs(F.relations) do
    local route = {source = mapped_font(locale, source) or source, targets = {}}
    key[#key + 1], key[#key + 2] = locale, route.source
    for _, target in ipairs(targets) do
      local id = mapped_font(target, source)
      if id then
        route.targets[#route.targets + 1] = id
        key[#key + 1] = id
      end
    end
    key[#key + 1] = '/'
    routes[locale] = route
  end
  key = table.concat(key, ':')
  local context = F.context_ids[key]
  if not context then
    context = #F.contexts + 1
    F.contexts[context], F.context_ids[key] = routes, context
  end
  tex.setattribute(F.attribute, context)
end

function F.process(head)
  local in_math = false
  for item in node.traverse(head) do
    if item.id == math_node then
      in_math = item.subtype == 0
    elseif not in_math and item.id == disc then
      item.pre = item.pre and F.process(item.pre)
      item.post = item.post and F.process(item.post)
      item.replace = item.replace and F.process(item.replace)
    elseif not in_math and item.id == glyph then
      local context = F.contexts[node.get_attribute(item, F.attribute)]
      local locale = node.get_attribute(item, Babel.attr_locale)
      local route = context and context[locale]
      if route and item.font == route.source then
        local current = font.getfont(item.font)
        if current and not current.characters[item.char] then
          for _, id in ipairs(route.targets) do
            local target = font.getfont(id)
            if target and target.characters[item.char] then
              item.font = id
              break
            end
          end
        end
      end
    end
  end
  return head
end

function F.install()
  if not F.installed then
    luatexbase.add_to_callback('pre_shaping_filter', F.process, 'babelbidi.font-fallback')
    F.installed = true
  end
end

return F
