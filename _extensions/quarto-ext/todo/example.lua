local function createLinkWithClass(text, link_target)
    link = pandoc.Link(text, link_target, text, {class = "example"})
    return link
end

return {
  ["example-code"] = function(args, kwargs)
    name = pandoc.utils.stringify(args[1])
    href = [[https://github.com/JanCaha/PyQt-GIS-book/tree/main/examples/]] .. name  
    return createLinkWithClass(name, href)
  end
}