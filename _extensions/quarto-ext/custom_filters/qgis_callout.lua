function Div(el)
  if quarto.doc.isFormat("html:js") then
    if el.classes:includes('qgis') then
      text1 = [[<div class="callout-qgis callout callout-style-default callout-captioned">
  <div class="callout-header d-flex align-content-center">
  <div class="callout-icon-container">
  <i class="callout-icon"></i>
  </div>
  <div class="callout-caption-container flex-fill">
  QGIS
  </div>
  </div>
  <div class="callout-body-container callout-body">
  <p>]]
      text2 = [[</p>
      </div>
      </div>]]

      local divQgis = pandoc.Div({})
      divQgis.content:insert(pandoc.RawInline('html', text1))
      for i=1,#el.content do  
        divQgis.content:insert(el.content[i]) 
      end
      divQgis.content:insert(pandoc.RawInline('html', text2))
      -- quarto.utils.dump(divQgis)
      -- quarto.utils.dump(el)
      return divQgis
    end
    return el
  end
  return el
end
