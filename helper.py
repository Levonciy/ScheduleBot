import Types
    
def find(src: Types.OptionCollection, id: int):
    name = "&lt;no data&gt;"
    
    for opt in src:
        if opt.id == id: name = opt.name; break
        
    return name