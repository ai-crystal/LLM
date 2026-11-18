-- 把 Markdown 的 ::: {.keypoint} 块转换成 LaTeX 的 keybox 环境
function Div(el)
  if el.classes:includes("keypoint") then
    local out = pandoc.List()
    out:insert(pandoc.RawBlock("latex", "\\begin{keybox}"))
    out:extend(el.content)
    out:insert(pandoc.RawBlock("latex", "\\end{keybox}"))
    return out
  end
  if el.classes:includes("partintro") then
    local out = pandoc.List()
    out:insert(pandoc.RawBlock("latex", "\\begin{partintro}"))
    out:extend(el.content)
    out:insert(pandoc.RawBlock("latex", "\\end{partintro}"))
    return out
  end
end
