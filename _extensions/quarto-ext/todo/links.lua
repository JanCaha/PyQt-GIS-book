local function removePrefix(s)
    return s:gsub("pyqt5%.", "")
end

local function removeBrackets(s)
    return s:gsub("%(", ""):gsub("%)", "")
end

local function createLinkWithClass(text, link_target)
    code = pandoc.Code(text)
    link = pandoc.Link(code, link_target, text, {class = "documentation"})
    return link
end

return {
  ["python-module"] = function(args, kwargs)
    name = pandoc.utils.stringify(args[1])
    href = [[https://docs.python.org/3.8/library/]] .. name .. [[.html]]  
    return createLinkWithClass(name, href)
  end,

  ["python-class"] = function(args, kwargs)
    name = pandoc.utils.stringify(args[1])
    python_module = pandoc.utils.stringify(args[2])
    href = [[https://docs.python.org/3.8/library/]] .. python_module .. [[.html]]

    if #args == 3 then
      specification = pandoc.utils.stringify(args[3])
      href = href .. "#" .. specification
    end
    
    return createLinkWithClass(name, href)
  end,

  ["qt-class"] = function(args, kwargs)
    name_orig = pandoc.utils.stringify(args[1])
    name = string.lower(name_orig)
    name = removeBrackets(name)
    href = [[https://doc.qt.io/qt-5/]] .. name .. [[.html]]
    return createLinkWithClass(name_orig, href)
  end,

  ["qt-module"] = function(args, kwargs)
    name_orig = pandoc.utils.stringify(args[1])
    name = removePrefix(string.lower(name_orig))
    href = [[https://doc.qt.io/qt-5/]] .. name .. [[-index.html]]
    return createLinkWithClass(name_orig, href)
  end
}

